import cookielib
import requests
import logging
import os
import json
from .config import config, CONFIG_FOLDER

BASE_URL = 'https://leetcode.com'
LOGIN_URL = BASE_URL + '/accounts/login/'
API_URL = BASE_URL + '/api/problems/algorithms/'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
    'Connection': 'keep-alive',
    'Host': 'leetcode.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
    'Referer': 'https://leetcode.com/accounts/login/',
}

requests = requests.Session()
requests.cookies = cookielib.LWPCookieJar(os.path.join(CONFIG_FOLDER, 'cookies'))
try:
    requests.cookies.load(ignore_discard=True)
except:
    pass

class NetworkError(Exception):
    def __init__(self, message, code):
        if not isinstance(message, str) or message == '':
            self.message = 'Network error!'
        else:
            self.message = '%s code: %d' % (message, code)
        print self.message

def login():
    logger = logging.getLogger(__name__)
    if not config.username or not config.password:
        return False
    login_data = {}
    r = requests.get(LOGIN_URL, headers=headers)
    if r.status_code != 200:
        logger.error('login failed')
        return False
    csrftoken = r.cookies['csrftoken']
    login_data['csrfmiddlewaretoken'] = csrftoken
    login_data['login'] = config.username
    login_data['password'] = config.password
    login_data['remember'] = 'on'
    r = requests.post(LOGIN_URL, headers=headers, data=login_data)
    if r.status_code != 200:
        logger.error('login failed')
        return False

    logger.info("login success")
    requests.cookies.save()
    return True

def is_login():
    r = requests.get(API_URL, headers=headers)
    if r.status_code != 200:
        return False
    text = r.text.encode('utf-8')
    data = json.loads(text)
    return data['user_name'] != ''
