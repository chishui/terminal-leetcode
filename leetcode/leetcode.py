import os
import re
import requests
import logging
from bs4 import BeautifulSoup
from .config import Config
from .model import QuizItem

BASE_URL = 'https://leetcode.com'
HOME_URL = BASE_URL + '/problemset/algorithms'
LOGIN_URL = BASE_URL + '/accounts/login/'
HOME = os.path.expanduser('~')
CONFIG = os.path.join(HOME, '.config', 'leetcode')
#logging.basicConfig(filename=os.path.join(CONFIG,'running.log'),format='%(asctime)s %(message)s',level=logging.DEBUG)

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
    'Connection': 'keep-alive',
    'Host': 'leetcode.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
    'Referer': 'https://leetcode.com/accounts/login/',
}

class Leetcode(object):
    def __init__(self):
        self.items = []
        self.config = Config()
        self.config.load()
        self.session = requests.session()
        self.cookies = None
        self.is_login = False

    def __getitem__(self, i):
        return self.items[i]

    @property
    def solved(self):
        return [i for i in self.items if i.pass_status == 'ac']

    def hard_retrieve_home(self):
        r, error = retrieve(self.session, HOME_URL)
        if error:
            return
        text = r.text.encode('utf-8')
        return self.parse_home(text)

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
        r, error = retrieve(self.session, BASE_URL + item.url)
        if error:
            return
        text = r.text.encode('utf-8')
        text = text.replace('<br>', '')
        bs = BeautifulSoup(text, 'lxml')
        content = bs.find('div', 'question-content')
        preprocess_bs(content)
        title = bs.find('div', 'question-title').h3.text
        body = content.text.replace(chr(13), '')
        body = re.sub('\n{3,}', '\n\n', body)
        # get sample code
        rawCode = bs.find("div", attrs={"ng-controller": "AceCtrl as aceCtrl"}).attrs["ng-init"]
        language = format_language_text(self.config.language)
        pattern = "\\'text\\':\s\\'%s\\',\s\\'defaultCode\\':\s\\'(.*?)\\'" % language
        content = re.search(pattern, rawCode).group(1).\
              encode("utf-8").decode("unicode-escape").\
              replace("\r\n", "\n")
        return title, body, content

    def login(self):
        global headers
        if not self.config.username or not self.config.password:
            return False

        login_data = {}
        res, error = retrieve(self.session, LOGIN_URL, headers)
        if error:
            return False
        csrftoken = res.cookies['csrftoken']
        login_data['csrfmiddlewaretoken'] = csrftoken
        login_data['login'] = self.config.username
        login_data['password'] = self.config.password
        login_data['remember'] = "on"
        res, error = retrieve(self.session, LOGIN_URL, headers=headers, method='POST', data=login_data)
        if error:
            return False

        self.cookies = dict(self.session.cookies)
        self.is_login = True
        return True

def preprocess_bs(bs):
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
            return ("Error: status code=%s" % r.status_code, True)
        else:
            return (r, False)
    except requests.exceptions.RequestException as e:
            return ("Error: {}".format(e), True)

def format_language_text(language):
    language = language.replace('+', '\+')
    language = language.replace('#', '\#')
    return language
