import unittest
import os
from unittest import mock
from leetcode.auth import *
from leetcode.config import *
import requests_mock

class TestAuth(unittest.TestCase):
    
    def setUp(self):
        self.auth = Auth()

    def test_retrieve(self):
        with requests_mock.Mocker() as m:
            m.get(API_URL, exc=requests.exceptions.ConnectTimeout)
            with self.assertRaises(NetworkError):
                r = self.auth.retrieve(API_URL)

            m.get(API_URL, exc=requests.exceptions.RequestException)
            with self.assertRaises(NetworkError):
                r = self.auth.retrieve(API_URL)
