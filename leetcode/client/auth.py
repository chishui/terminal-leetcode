import requests
import logging
import os
import json
from http import cookiejar
from ..helper.config import config, CONFIG_FOLDER
from ..helper.trace import trace

BASE_URL = 'https://leetcode.com'
LOGIN_URL = BASE_URL + '/accounts/login/'
API_URL = BASE_URL + '/api/problems/all/'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6',
    'Host': 'leetcode.com',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Mobile Safari/537.36',
    'Referer': 'https://leetcode.com/accounts/login/',
}

logger = logging.getLogger(__name__)


class Auth(object):
    def __init__(self):
        self.cookies = None
        self.get_cookies_from_chrome()

    def get_cookies_from_local_file(self):
        COOKIE_PATH = os.path.join(CONFIG_FOLDER, 'cookies')
        self.cookies = cookiejar.FileCookieJar(COOKIE_PATH)
        try:
            self.cookies.load(ignore_discard=True)
        except Exception:
            pass

    def get_cookies_from_chrome(self):
        try:
            from pycookiecheat import chrome_cookies
            self.cookies = chrome_cookies(BASE_URL)
        except Exception:
            logger.error("Cannot get cookies from chrome")

    @trace
    def login(self):
        logger = logging.getLogger(__name__)
        if not config.username or not config.password:
            return False
        login_data = {}
        r = self.retrieve(LOGIN_URL, headers=headers)
        if r.status_code != 200:
            logger.error('login failed')
            return False
        if 'csrftoken' in r.cookies:
            csrftoken = r.cookies['csrftoken']
            login_data['csrfmiddlewaretoken'] = csrftoken
        login_data['login'] = config.username
        login_data['password'] = config.password
        login_data['remember'] = 'on'

        request_headers = {"Accept": "*/*", "DNT": "1", "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary725gDSRiGxbNlBGY"}
        request_headers.update(headers)
        r = self.retrieve(LOGIN_URL, method='POST', headers=request_headers, data=json.dumps(login_data))
        logger.info(r.text)
        logger.info(r.content)
        if r.status_code != 200:
            logger.error('login failed')
            return False

        logger.info("login success")
        # session.cookies.save()
        return True

    @trace
    def is_login(self):
        r = self.retrieve(API_URL, headers=headers)
        if r.status_code != 200:
            return False
        text = r.content
        data = json.loads(text)
        return 'user_name' in data and data['user_name'] != ''

    @trace
    def retrieve(self, url, headers=None, method='GET', data=None):
        r = None
        try:
            if method == 'GET':
                r = requests.get(url, headers=headers, cookies=self.cookies)
            elif method == 'POST':
                r = requests.post(url, headers=headers, data=data, cookies=self.cookies)
            if r.status_code != 200:
                logger.info(r.text)
            return r
        except requests.exceptions.RequestException:
            if r:
                raise NetworkError('Network error: url: %s' % url, r.status_code)
            else:
                raise NetworkError('Network error: url: %s' % url)


class NetworkError(Exception):
    def __init__(self, message, code=0):
        if not message or message == '':
            self.message = 'Network error!'
        else:
            self.message = '%s code: %d' % (message, code)
        logger.error(self.message)
