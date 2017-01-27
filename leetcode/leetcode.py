import os
import re
import json
import logging
from bs4 import BeautifulSoup
from .config import config
from .model import QuizItem
from .auth import requests, is_login, headers, NetworkError

BASE_URL = 'https://leetcode.com'
API_URL = BASE_URL + '/api/problems/algorithms/'
HOME_URL = BASE_URL + '/problemset/algorithms'

class Leetcode(object):
    def __init__(self):
        self.items = []
        self.logger = logging.getLogger(__name__)
        config.load()
        self.is_login = is_login()
        self.logger.debug("is login: %s", self.is_login)

    def __getitem__(self, i):
        return self.items[i]

    @property
    def solved(self):
        return [i for i in self.items if i.pass_status == 'ac']

    def hard_retrieve_home(self):
        r = retrieve(requests, API_URL)
        text = r.text.encode('utf-8')
        return self.parse_home_API(text)

    def parse_home_API(self, text):
        difficulty = {1: "Easy", 2: "Medium", 3: "Hard"}
        self.items = []
        json_data = json.loads(text)
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
        r = retrieve(requests, BASE_URL + item.url)
        text = r.text.encode('utf-8')
        text = text.replace('<br>', '')
        bs = BeautifulSoup(text, 'lxml')

        if bs.find('form', 'form-signin'):
            self.session.cookies.clear()
            r = retrieve(requests, BASE_URL + item.url)

        content = bs.find('div', 'question-content')
        preprocess_bs(content)
        title = bs.find('div', 'question-title').h3.text.strip()
        body = content.text.replace(chr(13), '')
        body = re.sub('\n{3,}', '\n\n', body).strip()
        # get sample code
        rawCode = bs.find("div", attrs={"ng-controller": "AceCtrl as aceCtrl"}).attrs["ng-init"]
        language = format_language_text(config.language)
        pattern = "\\'text\\':\s\\'%s\\',\s\\'defaultCode\\':\s\\'(.*?)\\'" % language
        content = re.search(pattern, rawCode).group(1).\
              encode("utf-8").decode("unicode-escape").\
              replace("\r\n", "\n")
        return title, body, content


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

def retrieve(session, url, headers=None, method='GET', data=None):
    try:
        if method == 'GET':
            r = session.get(url, headers=headers)
        elif method == 'POST':
            r = session.post(url, headers=headers, data=data)
        if r.status_code != 200:
            raise NetworkError('Network error: url: %s' % url, r.status_code)
        else:
            return r
    except requests.exceptions.RequestException as e:
        raise NetworkError('Network error: url: %s' % url, r.status_code)

def format_language_text(language):
    language = language.replace('+', '\+')
    language = language.replace('#', '\#')
    return language
