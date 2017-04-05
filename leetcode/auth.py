import cookielib
import requests
import logging
import os
import json
from .config import config, CONFIG_FOLDER

BASE_URL = 'https://leetcode.com'
LOGIN_URL = BASE_URL + '/accounts/login/'
API_URL = BASE_URL + '/api/problems/algorithms/'

COOKIE_PATH = os.path.join(CONFIG_FOLDER, 'cookies')

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
    'Connection': 'keep-alive',
    'Host': 'leetcode.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
    'Referer': 'https://leetcode.com/accounts/login/',
}

session = requests.Session()
session.cookies = cookielib.LWPCookieJar(COOKIE_PATH)
try:
    session.cookies.load(ignore_discard=True)
except:
    pass

logger = logging.getLogger(__name__)

class NetworkError(Exception):
    def __init__(self, message, code=0):
        if not message or message == '':
            self.message = 'Network error!'
        else:
            self.message = '%s code: %d' % (message, code)
        logger.error(self.message)

def login():
    logger = logging.getLogger(__name__)
    if not config.username or not config.password:
        return False
    login_data = {}
    r = retrieve(LOGIN_URL, headers=headers)
    if r.status_code != 200:
        logger.error('login failed')
        return False
    if 'csrftoken' in r.cookies:
        csrftoken = r.cookies['csrftoken']
        login_data['csrfmiddlewaretoken'] = csrftoken
    login_data['login'] = config.username
    login_data['password'] = config.password
    login_data['remember'] = 'on'
    r = retrieve(LOGIN_URL, method='POST', headers=headers, data=login_data)
    if r.status_code != 200:
        logger.error('login failed')
        return False

    logger.info("login success")
    session.cookies.save()
    return True

def is_login():
    r = retrieve(API_URL, headers=headers)
    if r.status_code != 200:
        return False
    text = r.text.encode('utf-8')
    data = json.loads(text)
    return 'user_name' in data and data['user_name'] != ''


def retrieve(url, headers=None, method='GET', data=None):
    try:
        if method == 'GET':
            r = session.get(url, headers=headers)
        elif method == 'POST':
            r = session.post(url, headers=headers, data=data)
        return r
    except requests.exceptions.RequestException as e:
        raise NetworkError('Network error: url: %s' % url)
