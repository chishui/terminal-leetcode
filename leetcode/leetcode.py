import os
import re
import json
import logging
from bs4 import BeautifulSoup
from .config import config
from .auth import session, headers, retrieve
from .code import *

BASE_URL = 'https://leetcode.com'
API_URL = BASE_URL + '/api/problems/algorithms/'
HOME_URL = BASE_URL + '/problemset/algorithms'
SUBMISSION_URL = BASE_URL + '/submissions/detail/{id}/check/'

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z

LANG_MAPPING = {
    'C++': 'cpp',
    'Python': 'python',
    'Java': 'java',
    'C': 'c',
    'C#': 'csharp',
    'Javascript': 'javascript',
    'Ruby': 'ruby',
    'Swift': 'swift',
    'Go': 'go',
}

class Quiz(object):
    def __init__(self):
        self.id = None
        self.title = None
        self.content = None
        self.sample_code = None
        self.locked = False
        self.difficulty = None
        self.acceptance = None
        self.submission_status = None
        self.favorite = None
        self.url = None
        self.discussion_url = None
        self.tags = []
        self.html_content = None
        self.logger = logging.getLogger(__name__)

    def load(self):
        r = retrieve(self.url)
        if r.status_code != 200:
            return False
        text = r.text.encode('utf-8')
        text = text.replace('<br>', '')
        bs = BeautifulSoup(text, 'lxml')

        if bs.find('form', 'form-signin'):
            self.session.cookies.clear()
            r = retrieve(BASE_URL + item.url)

        try:
            content = bs.find('div', 'question-description')
            self.html_content = str(content)
            self.title = bs.find('div', 'question-title').h3.text.strip()
            self.content = content.text.replace(chr(13), '')
            self.content = re.sub('\n{3,}', '\n\n', self.content).strip()
            a = bs.find('section', {'class': 'action-btn-set'})

            self.tags = []
            tag = bs.find('div', {'id': 'tags-topics'})
            if tag:
                tagas = tag.find_all('a')
                for taga in tagas:
                    self.tags.append(taga.text)

            for child in a:
                if child.name is 'a' and child.text.strip() == 'Discuss':
                    self.discussion_url = child['href']

            # get sample code
            language = format_language_text(config.language)
            pattern = "\\'text\\':\s\\'%s\\',\s\\'defaultCode\\':\s\\'(.*?)\\'" % language
            self.sample_code = re.search(pattern, bs.prettify()).group(1).\
                  encode("utf-8").decode("unicode-escape").\
                  replace("\r\n", "\n")
            return True
        except AttributeError, e:
            self.logger.error(e)
            return False

    def submit(self, code):
        body = { 'question_id': self.id,
                'test_mode': False,
                'lang': LANG_MAPPING.get(config.language, 'cpp'),
                'judge_type': 'large',
                'typed_code': code}

        csrftoken = ''
        for ck in session.cookies:
            if ck.name == 'csrftoken':
                csrftoken = ck.value

        newheaders = merge_two_dicts(headers, {'Origin': BASE_URL,
            'Referer': self.url + '/?tab=Description',
            'DNT': '1',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'})

        r = retrieve(self.url + '/submit/', method='POST', data=json.dumps(body), headers=newheaders)
        if r.status_code != 200:
            return (False, 'Request failed!')
        text = r.text.encode('utf-8')
        try:
            data = json.loads(text)
        except:
            return (False, text)

        if 'error' in data:
            return (False, data['error'])
        return (True, data['submission_id'])

    def check_submission_result(self, submission_id):
        url = SUBMISSION_URL.format(id=submission_id)
        r = retrieve(url)
        if r.status_code != 200:
            return (-100, 'Request failed!')
        text = r.text.encode('utf-8')
        data = json.loads(text)
        try:
            if data['state'] == 'PENDING':
                return (1,)
            elif data['state'] == 'STARTED':
                return (2,)
            elif data['state'] == 'SUCCESS':
                if 'run_success' in data:
                    if data['run_success']:
                        return (0, data)#data['total_correct'], data['total_testcases'], data['status_runtime'])
                    else:
                        return (-1, data)#data['compile_error'])
                else:
                    raise KeyError
        except KeyError:
            return (-2, 'Unknow error')


class Leetcode(object):
    def __init__(self):
        self.quizzes = []
        self.logger = logging.getLogger(__name__)
        config.load()
        self.is_login = False

    def __getitem__(self, i):
        return self.quizzes[i]

    @property
    def solved(self):
        return [i for i in self.quizzes if i.submission_status == 'ac']

    def load(self):
        r = retrieve(API_URL)
        if r.status_code != 200:
            return None
        text = r.text.encode('utf-8')
        return self._parse_home_API(text)

    def _parse_home_API(self, text):
        difficulty = {1: "Easy", 2: "Medium", 3: "Hard"}
        self.quizzes = []
        json_data = json.loads(text)

        try:
            for quiz in json_data['stat_status_pairs']:
                if quiz['stat']['question__hide']:
                    continue

                data = Quiz()
                data.title = quiz['stat']['question__title']
                data.id = quiz['stat']['question_id']
                data.locked = not json_data['is_paid'] and quiz['paid_only']
                data.difficulty = difficulty[quiz['difficulty']['level']]
                data.favorite = quiz['is_favor']
                data.acceptance = "%.1f%%" % (float(quiz['stat']['total_acs']) * 100 / float(quiz['stat']['total_submitted']))
                data.url = BASE_URL + "/problems/" + quiz['stat']['question__title_slug']
                data.submission_status = quiz['status']
                self.quizzes.append(data)
            return self.quizzes
        except (KeyError, AttributeError) as e:
            self.logger.error(e)

def format_language_text(language):
    language = language.replace('+', '\+')
    language = language.replace('#', '\#')
    return language

