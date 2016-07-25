import os
import re
import requests
from bs4 import BeautifulSoup
from .config import Config
from .model import QuizItem

BASE_URL = 'https://leetcode.com'
HOME_URL = BASE_URL + '/problemset/algorithms'
LOGIN_URL = BASE_URL + '/accounts/login/'
HOME = os.path.expanduser('~')
CONFIG = os.path.join(HOME, '.config', 'leetcode')
DATA_FILE = os.path.join(CONFIG, 'leetcode_home.txt')

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
        text = self.retrieve(HOME_URL).encode('utf-8')
        save_data_to_file(text, DATA_FILE)
        return self.parse_home(text)

    def retrieve_home(self):
        if not os.path.exists(DATA_FILE):
            return self.hard_retrieve_home()
        text = load_data_from_file(DATA_FILE)
        return self.parse_home(text)

    def parse_home(self, text):
        bs = BeautifulSoup(text, 'html.parser')
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
        text = self.retrieve(BASE_URL + item.url).encode('utf-8')
        bs = BeautifulSoup(text, 'html.parser')
        title = bs.find('div', 'question-title').h3.text
        body = bs.find('div', 'question-content').text.replace(chr(13), '')
        # get sample code
        rawCode = bs.find("div", attrs={"ng-controller": "AceCtrl as aceCtrl"}).attrs["ng-init"]
        language = format_language_text(self.config.language)
        pattern = "\\'text\\':\s\\'%s\\',\s\\'defaultCode\\':\s\\'(.*?)\\'" % language
        content = re.search(pattern, rawCode).group(1).\
              encode("utf-8").decode("unicode-escape").\
              replace("\r\n", "\n")
        body += '\n\n--SAMPLE CODE--\n\n' + content
        item.sample_code = content
        return title, body

    def login(self):
        if not self.config.username or not self.config.password:
            return False

        login_data = {}
        res = self.session.get(url=LOGIN_URL, headers=headers)
        csrftoken = res.cookies['csrftoken']
        login_data['csrfmiddlewaretoken'] = csrftoken
        login_data['login'] = self.config.username
        login_data['password'] = self.config.password
        login_data['remember'] = "on"
        res = self.session.post(LOGIN_URL, headers=headers, data=login_data)
        if res.status_code != 200:
            return False

        self.cookies = dict(self.session.cookies)
        self.is_login = True

    def retrieve(self, url):
        r = self.session.get(url)
        if r.status_code != 200:
            return None

        return r.text

def format_language_text(language):
    language = language.replace('+', '\+')
    language = language.replace('#', '\#')
    return language

def save_data_to_file(data, filename):
    filepath = os.path.dirname(filename)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    with open(filename, 'w') as f:
        f.write(data)

def load_data_from_file(path):
    with open(path, 'r') as f:
        return f.read()
