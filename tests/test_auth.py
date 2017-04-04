import unittest
import os
import mock
from leetcode.auth import *
from leetcode.config import *

class TestAuth(unittest.TestCase):
    @mock.patch('leetcode.auth.config')
    @mock.patch('leetcode.auth.requests.post')
    @mock.patch('leetcode.auth.requests.get')
    def test_login(self, mock_get, mock_post, mock_config):
        mock_config.username = None
        self.assertFalse(login())

        mock_config.username = 'chishui2'
        mock_config.username = 'xly84610'
        mock_get.return_value.status_code = 403
        self.assertFalse(login())

        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 403
        self.assertFalse(login())

        mock_post.return_value.status_code = 200
        self.assertTrue(login())

    @mock.patch('leetcode.auth.requests.get')
    def test_is_login(self, mock_get):
        mock_get.return_value.status_code = 400
        self.assertFalse(is_login())

        mock_get.return_value.status_code = 200
        mock_get.return_value.text = ' { "user_name": "chishui" } '
        self.assertTrue(is_login())

        mock_get.return_value.text = ' { "user": "chishui" } '
        self.assertFalse(is_login())
