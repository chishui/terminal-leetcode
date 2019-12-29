import unittest
from leetcode.leetcode import *
from leetcode.quiz import Quiz
from leetcode.auth import Auth
from leetcode.auth import NetworkError
from unittest.mock import patch
from leetcode.common import SUBMISSION_URL
import requests_mock
import requests

class TestLeetcode(unittest.TestCase):
    def setUp(self):
        self.auth = Auth()
        self.leet = Leetcode(self.auth)

    def test_retrieve_home(self):
        data = {
  "frequency_mid": 0,
  "num_solved": 0,
  "category_slug": "algorithms",
  "stat_status_pairs": [
    {
      "status": None,
      "stat": {
        "total_acs": 695,
        "question__title": "Split Array with Equal Sum",
        "is_new_question": True,
        "question__article__slug": "split-array-with-equal-sum",
        "total_submitted": 2793,
        "question__title_slug": "split-array-with-equal-sum",
        "question__article__live": True,
        "question__hide": False,
        "question_id": 548
      },
      "is_favor": False,
      "paid_only": True,
      "difficulty": {
        "level": 2
      },
      "frequency": 0,
      "progress": 0
    },
    {
      "status": None,
      "stat": {
        "total_acs": 1602,
        "question__title": "Friend Circles",
        "is_new_question": False,
        "question__article__slug": "friend-circles",
        "total_submitted": 3351,
        "question__title_slug": "friend-circles",
        "question__article__live": True,
        "question__hide": False,
        "question_id": 547
      },
      "is_favor": False,
      "paid_only": False,
      "difficulty": {
        "level": 2
      },
      "frequency": 0,
      "progress": 0
    }
],
"is_paid": False,
  "frequency_high": 0,
  "user_name": "",
  "num_total": 507
}

        with requests_mock.Mocker() as m:
            m.get(API_URL, status_code=403)
            self.assertIsNone(self.leet.load())
            m.get(API_URL, json={"error": "not found"})
            self.assertIsNone(self.leet.load())
            m.get(API_URL, json=data)
            items = self.leet.load()
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0].id, 548)
            self.assertEqual(items[0].difficulty, 'Medium')

    def test_submit_code(self):
        item = Quiz(self.auth)
        item.id = 1
        item.url = 'http://hello.com'
        item.title = ''
        item.acceptance = ''
        item.difficulty = 'Easy'
        item.locked = True
        item.submission_status = 'ac'

        with requests_mock.Mocker() as m:
            m.post(item.url + '/submit/', status_code=402)
            self.assertFalse(item.submit('code')[0])

            m.post(item.url + '/submit/', text='{"error": "1"}')
            self.assertFalse(item.submit('code')[0])

            m.post(item.url + '/submit/', text='{"submission_id": 1}')
            self.assertTrue(item.submit('code')[0])

    def test_submission_result(self):
        item = Quiz(self.auth)
        item.id = 1
        item.url = 'http://hello.com'
        item.title = ''
        item.acceptance = ''
        item.difficulty = 'Easy'
        item.locked = True
        item.submission_status = 'ac'
        url = SUBMISSION_URL.format(id=1)
        with requests_mock.Mocker() as m:
            m.get(url, status_code=403)
            self.assertEqual(item.check_submission_result(1)[0], -100)
            m.get(url, json={ 'state': 'PENDING' })
            self.assertEqual(item.check_submission_result(1)[0], 1)
            m.get(url, json={ 'state': 'STARTED' })
            self.assertEqual(item.check_submission_result(1)[0], 2)
            m.get(url, json={ 'state': 'SUCCESS' })
            self.assertEqual(item.check_submission_result(1)[0], -2)
            m.get(url, json={ 'state': 'SUCCESS', 'run_success': False})
            self.assertEqual(item.check_submission_result(1)[0], -1)
            m.get(url, json={ 'state': 'SUCCESS', 'run_success': True})
            self.assertEqual(item.check_submission_result(1)[0], 0)
            m.get(url, json={ 'state': 'SUCCESS', 'run_success': True, 'total_correct':0, 'total_testcases': 0, 'status_runtime': 0})
            self.assertEqual(item.check_submission_result(1)[0], 0)

