import os
import re
import json
import logging
from bs4 import BeautifulSoup
from .config import config
from .model import QuizItem, DetailData
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

class Leetcode(object):
    def __init__(self):
        self.items = []
        self.logger = logging.getLogger(__name__)
        config.load()
        self.is_login = False

    def __getitem__(self, i):
        return self.items[i]

    @property
    def solved(self):
        return [i for i in self.items if i.pass_status == 'ac']

    def hard_retrieve_home(self):
        r = retrieve(API_URL)
        if r.status_code != 200:
            return None
        text = r.text.encode('utf-8')
        return self.parse_home_API(text)

    def parse_home_API(self, text):
        difficulty = {1: "Easy", 2: "Medium", 3: "Hard"}
        self.items = []
        json_data = json.loads(text)

        try:
            for quiz in json_data['stat_status_pairs']:
                if quiz['stat']['question__hide']:
                    continue

                data = {}
                data['title'] = quiz['stat']['question__title']
                data['id'] = quiz['stat']['question_id']
                data['lock'] = not json_data['is_paid'] and quiz['paid_only']
                data['difficulty'] = difficulty[quiz['difficulty']['level']]
                data['favorite'] = quiz['is_favor']
                data['acceptance'] = "%.1f%%" % (float(quiz['stat']['total_acs']) * 100 / float(quiz['stat']['total_submitted']))
                data['url'] = "/problems/" + quiz['stat']['question__title_slug']
                data['pass'] = quiz['status']
                item = QuizItem(data)
                self.items.append(item)
            return self.items
        except (KeyError, AttributeError) as e:
            self.logger.error(e)
            return None

    def parse_home(self, text):
        self.items = []
        bs = BeautifulSoup(text, 'lxml')
        trs = bs.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) < 3:
                continue
            data = {}
            data['pass'] = tds[0].span['class'][0]
            data['id'] = tds[1].text
            data['title'] = tds[2].a.text
            data['url'] = tds[2].a['href']
            data['acceptance'] = tds[3].text
            data['difficulty'] = tds[-1].text
            data['lock'] = tds[2].find('i', 'fa-lock') != None
            item = QuizItem(data)
            self.items.append(item)

        return self.items

    def retrieve_detail(self, item):
        r = retrieve(BASE_URL + item.url)
        if r.status_code != 200:
            return None
        text = r.text.encode('utf-8')
        text = text.replace('<br>', '')
        bs = BeautifulSoup(text, 'lxml')

        if bs.find('form', 'form-signin'):
            self.session.cookies.clear()
            r = retrieve(BASE_URL + item.url)

        try:
            content = bs.find('div', 'question-content')
            preprocess_bs(content)
            title = bs.find('div', 'question-title').h3.text.strip()
            body = content.text.replace(chr(13), '')
            body = re.sub('\n{3,}', '\n\n', body).strip()
            a = bs.find('section', {'class': 'action'})
            discussion_url = None
            for child in a:
                if child.name is 'a' and child.text.strip() == 'Discuss':
                    discussion_url = child['href']

            # get sample code
            language = format_language_text(config.language)
            pattern = "\\'text\\':\s\\'%s\\',\s\\'defaultCode\\':\s\\'(.*?)\\'" % language
            content = re.search(pattern, bs.prettify()).group(1).\
                  encode("utf-8").decode("unicode-escape").\
                  replace("\r\n", "\n")
            data = DetailData(title=title, body=body, code=content, discussion_url=discussion_url)
            return data
        except AttributeError, e:
            self.logger.error(e)
            return None

    def submit_code(self, item):
        filepath = get_code_file_path(item.id)
        if not os.path.exists(filepath):
            return (False, 'code file not exist!')
        code = get_code_for_submission(filepath)
        code = code.replace('\n', '\r\n')
        body = { 'question_id': item.id,
                'test_mode': False,
                'lang': LANG_MAPPING.get(config.language, 'cpp'),
                'judge_type': 'large',
                'typed_code': code}

        csrftoken = ''
        for ck in session.cookies:
            if ck.name == 'csrftoken':
                csrftoken = ck.value

        newheaders = merge_two_dicts(headers, {'Origin': BASE_URL,
            'Referer': BASE_URL + item.url + '/?tab=Description',
            'DNT': '1',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'})

        r = retrieve(BASE_URL + item.url + '/submit/', method='POST', data=json.dumps(body), headers=newheaders)
        if r.status_code != 200:
            return (False, 'Request failed!')
        text = r.text.encode('utf-8')
        data = json.loads(text)

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
                        return (0, data['total_correct'], data['total_testcases'], data['status_runtime'])
                    else:
                        return (-1, data['compile_error'])
                else:
                    raise KeyError
        except KeyError:
            return (-1, 'Unknow error')


def preprocess_bs(bs):
    if not bs:
        return
    allbs = bs.find_all('b')
    for b in allbs:
        if b.text == 'Credits:':
            b.parent.extract()
    allas = bs.find_all('a')
    for a in allas:
        if a.text == 'Subscribe':
            a.parent.parent.extract()


def format_language_text(language):
    language = language.replace('+', '\+')
    language = language.replace('#', '\#')
    return language
