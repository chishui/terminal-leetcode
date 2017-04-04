import unittest
import mock
import responses
from leetcode.leetcode import *
from leetcode.auth import NetworkError

class TestLeetcode(unittest.TestCase):
    def setUp(self):
        self.leet = Leetcode()

    @mock.patch('leetcode.leetcode.requests.get')
    def test_retrieve(self, mock_requests):
        mock_requests.side_effect = requests.exceptions.RequestException()
        with self.assertRaises(NetworkError):
            r = retrieve(requests, 'http://127.0.0.1')

        mock_requests.side_effect = requests.exceptions.ConnectionError('bad error')
        with self.assertRaises(NetworkError):
            r = retrieve(requests, 'http://127.0.0.1')

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
        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            rsps.add(responses.GET, API_URL,
                      json={"error": "not found"}, status=404)
            rsps.add(responses.GET, API_URL,
                      json={"error": "not found"}, status=200)
            rsps.add(responses.GET, API_URL,
                      json=data, status=200)
            self.assertIsNone(self.leet.hard_retrieve_home())
            self.assertIsNone(self.leet.hard_retrieve_home())
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
        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            item = QuizItem({'id': 1,
                            'url': '/hello',
                            'title':'',
                            'acceptance':'',
                            'difficulty':'Easy',
                            'lock':True,
                            'pass': 'ac'})
            rsps.add(responses.GET, BASE_URL+'/hello',
                      json={"error": "not found"}, status=404)
            rsps.add(responses.GET, BASE_URL+'/hello',
                      body=data, status=200)
            rsps.add(responses.GET, BASE_URL+'/hello',
                      body=data2, status=200)
            rsps.add(responses.GET, BASE_URL+'/hello',
                      body=data3, status=200)
            self.assertIsNone(self.leet.retrieve_detail(item))
            self.assertIsNone(self.leet.retrieve_detail(item))
            self.assertIsNone(self.leet.retrieve_detail(item))
            a, b, c = self.leet.retrieve_detail(item)
            self.assertEqual(a, 'title')
            self.assertEqual(b, 'content')
            self.assertEqual(c, 'code')

