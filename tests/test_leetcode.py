import unittest
import mock
from leetcode.leetcode import *
from leetcode.auth import NetworkError
import requests_mock
import requests

class TestLeetcode(unittest.TestCase):
    def setUp(self):
        self.leet = Leetcode()

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
            self.assertIsNone(self.leet.hard_retrieve_home())
            m.get(API_URL, json={"error": "not found"})
            self.assertIsNone(self.leet.hard_retrieve_home())
            m.get(API_URL, json=data)
            items = self.leet.hard_retrieve_home()
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0].id, 548)
            self.assertEqual(items[0].difficulty, 'Medium')

    def test_retrieve_detail(self):
        data = ' <html> <head> </head> <body> </body> </html> '
        data2 = ' <html> <head> </head> <body><div class=question-content>hello</div> </body> </html> '
        data3 = ''' <html> <head> </head> <body>
        <div class=question-content>content</div>
        <div class=question-title>
            <h3>title</h3>
        </div>
        <div ng-controller="AceCtrl as aceCtrl" ng-init="aceCtrl.init(
        [{'value': 'cpp', 'text': 'C++', 'defaultCode': 'code'}])">
        </div>
        </body> </html> '''
        item = QuizItem({'id': 1,
                        'url': '/hello',
                        'title':'',
                        'acceptance':'',
                        'difficulty':'Easy',
                        'lock':True,
                        'pass': 'ac'})

        with requests_mock.Mocker() as m:
            m.get(BASE_URL + '/hello', status_code=403)
            self.assertIsNone(self.leet.retrieve_detail(item))
            item.url = '/data'
            m.get(BASE_URL + '/data', text=data)
            self.assertIsNone(self.leet.retrieve_detail(item))
            item.url = '/data2'
            m.get(BASE_URL + '/data2', text=data2)
            self.assertIsNone(self.leet.retrieve_detail(item))
            item.url = '/data3'
            m.get(BASE_URL + '/data3', text=data3)
            a, b, c = self.leet.retrieve_detail(item)
            self.assertEqual(a, 'title')
            self.assertEqual(b, 'content')
            self.assertEqual(c, 'code')

    @mock.patch('leetcode.leetcode.os.makedirs')
    @mock.patch('leetcode.leetcode.get_code_for_submission')
    @mock.patch('leetcode.leetcode.os.path.exists')
    def test_submit_code(self, mock_exists, mock_get_code, mock_makedirs):
        item = QuizItem({'id': 1,
                        'url': '/hello',
                        'title':'',
                        'acceptance':'',
                        'difficulty':'Easy',
                        'lock':True,
                        'pass': 'ac'})
        mock_exists.return_value = False
        self.assertFalse(self.leet.submit_code(item)[0])

        mock_exists.return_value = True
        mock_get_code.return_value = 'code'
        with requests_mock.Mocker() as m:
            m.post(BASE_URL + item.url + '/submit/', status_code=402)
            self.assertFalse(self.leet.submit_code(item)[0])

            m.post(BASE_URL + item.url + '/submit/', text='{"error": "1"}')
            self.assertFalse(self.leet.submit_code(item)[0])

            m.post(BASE_URL + item.url + '/submit/', text='{"submission_id": 1}')
            self.assertTrue(self.leet.submit_code(item)[0])

    def test_submission_result(self):
        url = SUBMISSION_URL.format(id=1)
        with requests_mock.Mocker() as m:
            m.get(url, status_code=403)
            self.assertEqual(self.leet.check_submission_result(1)[0], -100)
            m.get(url, json={ 'state': 'PENDING' })
            self.assertEqual(self.leet.check_submission_result(1)[0], 1)
            m.get(url, json={ 'state': 'STARTED' })
            self.assertEqual(self.leet.check_submission_result(1)[0], 2)
            m.get(url, json={ 'state': 'SUCCESS' })
            self.assertEqual(self.leet.check_submission_result(1)[0], -1)
            m.get(url, json={ 'state': 'SUCCESS', 'run_success': False})
            self.assertEqual(self.leet.check_submission_result(1)[0], -1)
            m.get(url, json={ 'state': 'SUCCESS', 'run_success': True})
            self.assertEqual(self.leet.check_submission_result(1)[0], -1)
            m.get(url, json={ 'state': 'SUCCESS', 'run_success': True, 'total_correct':0, 'total_testcases': 0, 'status_runtime': 0})
            self.assertEqual(self.leet.check_submission_result(1)[0], 0)

