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
            self.assertIsNone(self.leet.load())
            m.get(API_URL, json={"error": "not found"})
            self.assertIsNone(self.leet.load())
            m.get(API_URL, json=data)
            items = self.leet.load()
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0].id, 548)
            self.assertEqual(items[0].difficulty, 'Medium')

    def test_retrieve_detail(self):
        data = ' <html> <head> </head> <body> </body> </html> '
        data2 = ' <html> <head> </head> <body><div class=question-content>hello</div> </body> </html> '
        data3 = ''' <html> <head> </head> <body>
        <div class=question-description>content</div>
        <div class=question-title>
            <h3>title</h3>
        </div>
<section class="action-btn-set col-md-12">
    <a href="https://discuss.leetcode.com/category/9" target="_blank" onclick="ga('send', 'event', 'discuss', 'click', 'two-sum');" class="icon-btn">
      <i class="fa fa-commenting-o" aria-hidden="true"></i>Discuss
    </a>
    <a href="/problems/random-one-question/" onclick="ga('send', 'event', 'pick-one-detail', 'click');" class="icon-btn">
      <i class="fa fa-random" aria-hidden="true"></i>Pick One
    </a>
    <button type="button" class="icon-btn" onclick="confirmations.confirm_see_solution(
              event,
              '/articles/two-sum/',
              false
              );">
      <i class="fa fa-book" aria-hidden="true"></i>Editorial Solution
    </button>
    <div id="question-detail-share-buttons" class="pull-right"><div data-reactroot=""><div class="share-button"><div class="SocialMediaShareButton SocialMediaShareButton--facebook"><div style="width: 32px; height: 32px;"><svg viewBox="0 0 64 64" fill="white" width="32" height="32" class="social-icon social-icon--facebook "><g><circle cx="32" cy="32" r="31" fill="#3b5998"></circle></g><g><path d="M34.1,47V33.3h4.6l0.7-5.3h-5.3v-3.4c0-1.5,0.4-2.6,2.6-2.6l2.8,0v-4.8c-0.5-0.1-2.2-0.2-4.1-0.2 c-4.1,0-6.9,2.5-6.9,7V28H24v5.3h4.6V47H34.1z"></path></g></svg></div></div></div><div class="share-button"><div class="SocialMediaShareButton SocialMediaShareButton--twitter"><div style="width: 32px; height: 32px;"><svg viewBox="0 0 64 64" fill="white" width="32" height="32" class="social-icon social-icon--twitter "><g><circle cx="32" cy="32" r="31" fill="#00aced"></circle></g><g><path d="M48,22.1c-1.2,0.5-2.4,0.9-3.8,1c1.4-0.8,2.4-2.1,2.9-3.6c-1.3,0.8-2.7,1.3-4.2,1.6 C41.7,19.8,40,19,38.2,19c-3.6,0-6.6,2.9-6.6,6.6c0,0.5,0.1,1,0.2,1.5c-5.5-0.3-10.3-2.9-13.5-6.9c-0.6,1-0.9,2.1-0.9,3.3 c0,2.3,1.2,4.3,2.9,5.5c-1.1,0-2.1-0.3-3-0.8c0,0,0,0.1,0,0.1c0,3.2,2.3,5.8,5.3,6.4c-0.6,0.1-1.1,0.2-1.7,0.2c-0.4,0-0.8,0-1.2-0.1 c0.8,2.6,3.3,4.5,6.1,4.6c-2.2,1.8-5.1,2.8-8.2,2.8c-0.5,0-1.1,0-1.6-0.1c2.9,1.9,6.4,2.9,10.1,2.9c12.1,0,18.7-10,18.7-18.7 c0-0.3,0-0.6,0-0.8C46,24.5,47.1,23.4,48,22.1z"></path></g></svg></div></div></div><div class="share-button"><div class="SocialMediaShareButton SocialMediaShareButton--googlePlus"><div style="width: 32px; height: 32px;"><svg viewBox="0 0 64 64" fill="white" width="32" height="32" class="social-icon social-icon--google "><g><circle cx="32" cy="32" r="31" fill="#dd4b39"></circle></g><g><path d="M25.3,30.1v3.8h6.3c-0.3,1.6-1.9,4.8-6.3,4.8c-3.8,0-6.9-3.1-6.9-7s3.1-7,6.9-7c2.2,0,3.6,0.9,4.4,1.7l3-2.9c-1.9-1.8-4.4-2.9-7.4-2.9c-6.1,0-11.1,5-11.1,11.1s5,11.1,11.1,11.1c6.4,0,10.7-4.5,10.7-10.9c0-0.7-0.1-1.3-0.2-1.8H25.3L25.3,30.1z M49.8,28.9h-3.2v-3.2h-3.2v3.2h-3.2v3.2h3.2v3.2h3.2v-3.2h3.2"></path></g></svg></div></div></div><div class="share-button"><div class="SocialMediaShareButton SocialMediaShareButton--linkedin"><div style="width: 32px; height: 32px;"><svg viewBox="0 0 64 64" fill="white" width="32" height="32" class="social-icon social-icon--linkedin "><g><circle cx="32" cy="32" r="31" fill="#007fb1"></circle></g><g><path d="M20.4,44h5.4V26.6h-5.4V44z M23.1,18c-1.7,0-3.1,1.4-3.1,3.1c0,1.7,1.4,3.1,3.1,3.1 c1.7,0,3.1-1.4,3.1-3.1C26.2,19.4,24.8,18,23.1,18z M39.5,26.2c-2.6,0-4.4,1.4-5.1,2.8h-0.1v-2.4h-5.2V44h5.4v-8.6 c0-2.3,0.4-4.5,3.2-4.5c2.8,0,2.8,2.6,2.8,4.6V44H46v-9.5C46,29.8,45,26.2,39.5,26.2z"></path></g></svg></div></div></div></div></div>
  </section>
        <div ng-controller="AceCtrl as aceCtrl" ng-init="aceCtrl.init(
        [{'value': 'cpp', 'text': 'C++', 'defaultCode': 'code'}])">
        </div>

<div id="tags-topics" class="hideout">
                    <a class="btn btn-xs btn-default btn-round text-sm" href="/tag/array/">Array</a>
                    <a class="btn btn-xs btn-default btn-round text-sm" href="/tag/hash-table/">Hash Table</a>
                  <br>
                </div>
        </body> </html> '''
        item = Quiz()
        item.id = 1
        item.url = 'http://hello.com'
        item.title = ''
        item.acceptance = ''
        item.difficulty = 'Easy'
        item.locked = True
        item.submission_status = 'ac'

        with requests_mock.Mocker() as m:
            m.get('http://hello.com', status_code=403)
            self.assertFalse(item.load())
            m.get('http://hello.com', text=data)
            self.assertFalse(item.load())
            m.get('http://hello.com', text=data2)
            self.assertFalse(item.load())
            m.get('http://hello.com', text=data3)
            item.load()
            self.assertEqual(item.title, 'title')
            self.assertEqual(item.content, 'content')
            self.assertEqual(item.sample_code, 'code')

    def test_submit_code(self):
        item = Quiz()
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
        item = Quiz()
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

