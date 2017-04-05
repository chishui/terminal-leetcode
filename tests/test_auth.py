import unittest
import os
import mock
from leetcode.auth import *
from leetcode.config import *
import requests_mock

class TestAuth(unittest.TestCase):

    def test_retrieve(self):
        with requests_mock.Mocker() as m:
            m.get(API_URL, exc=requests.exceptions.ConnectTimeout)
            with self.assertRaises(NetworkError):
                r = retrieve(API_URL)

            m.get(API_URL, exc=requests.exceptions.RequestException)
            with self.assertRaises(NetworkError):
                r = retrieve(API_URL)

    @mock.patch('leetcode.auth.session.cookies.save')
    @mock.patch('leetcode.auth.config')
    def test_login(self, mock_config, mock_save):
        mock_config.username = None
        self.assertFalse(login())

        mock_config.username = 'chishui2'
        mock_config.password = 'chishui2'
        with requests_mock.Mocker() as m:
            m.get(LOGIN_URL, status_code=403)
            self.assertFalse(login())
            m.get(LOGIN_URL, status_code=200)
            m.post(LOGIN_URL, status_code=403)
            self.assertFalse(login())

            m.get(LOGIN_URL, status_code=200)
            m.post(LOGIN_URL, status_code=200)
            self.assertTrue(login())

    @mock.patch('leetcode.auth.requests.get')
    def test_is_login(self, mock_get):
        with requests_mock.Mocker() as m:
            m.get(API_URL, status_code=403)
            self.assertFalse(is_login())

            m.get(API_URL, json={'user_name': 'chishui2'})
            self.assertTrue(is_login())

            m.get(API_URL, json={'user': 'chishui2'})
            self.assertFalse(is_login())
