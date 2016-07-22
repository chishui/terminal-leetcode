import os
import requests
from .model import QuizItem
from bs4 import BeautifulSoup

BASE_URL = 'https://leetcode.com'
HOME_URL = BASE_URL + '/problemset/algorithms'
HOME = os.path.expanduser('~')
CONFIG = os.path.join(HOME, '.config', 'leetcode')
DATA_FILE = os.path.join(CONFIG, 'leetcode_home.txt')

class Leetcode(object) :
    def __init__(self) :
        self.items = []

    def __getitem__(self, i) :
        return self.items[i]

    def hard_retrieve_home(self):
        text = retrieve(HOME_URL).encode('utf-8')
        save_data_to_file(text, DATA_FILE)
        return self.parse_home(text)

    def retrieve_home(self):
        if not os.path.exists(DATA_FILE):
            return self.hard_retrieve_home()
        text = load_data_from_file(DATA_FILE)
        return self.parse_home(text)

    def parse_home(self, text) :
        bs = BeautifulSoup(text, 'html.parser')
        items = []
        trs = bs.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if (len(tds) < 3):
                continue
            item = QuizItem(tds[1].text, tds[2].a.text, tds[2].a['href'], tds[3].text, tds[-1].text, tds[2].find('i', 'fa-lock') != None)
            self.items.append(item)

        return self.items

    def retrieve_detail(self, item):
        text = retrieve(BASE_URL + item.url).encode('utf-8')
        bs = BeautifulSoup(text, 'html.parser')
        title = bs.find('div', 'question-title').h3.text
        body = bs.find('div', 'question-content').text.replace(chr(13), '')
        return title, body


def retrieve(url) :
    r = requests.get(url)
    if r.status_code != 200:
        return None

    return r.text

def save_data_to_file(data, filename) :
    filepath = os.path.dirname(filename)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    with open(filename, 'w') as f:
        f.write(data)

def load_data_from_file(path) :
    with open(path, 'r') as f:
        return f.read()

