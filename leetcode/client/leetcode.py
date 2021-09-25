import json
import logging
from .auth import Auth, headers
from .quiz import Quiz
from ..helper.trace import trace
from ..helper.config import config
from ..helper.common import API_URL, BASE_URL, merge_two_dicts, GRAPHQL_URL


class Leetcode(object):
    def __init__(self):
        self.quizzes = []
        self.auth = Auth()
        self.logger = logging.getLogger(__name__)
        self.username = ""
        self.is_paid = False
        self.is_verified = False
        config.load()
        self.get_user()

    def __getitem__(self, i):
        return self.quizzes[i]

    @property
    def solved(self):
        return [i for i in self.quizzes if i.submission_status == 'ac']

    @property
    def is_login(self):
        return self.username != ""

    @trace
    def load(self):
        r = self.auth.retrieve(API_URL)
        if r.status_code != 200:
            return None
        return self._parse_home_API(r.text)

    def _parse_home_API(self, text):
        difficulty = {1: "Easy", 2: "Medium", 3: "Hard"}
        self.quizzes = []
        json_data = json.loads(text)

        try:
            for quiz in json_data['stat_status_pairs']:
                if quiz['stat']['question__hide']:
                    continue

                data = Quiz(self.auth)
                data.title = quiz['stat']['question__title']
                data.slug = quiz['stat']['question__title_slug']
                data.id = quiz['stat']['frontend_question_id']
                data.real_quiz_id = data.id # default real_quiz_id to frontend id
                data.locked = not self.is_paid and quiz['paid_only']
                data.difficulty = difficulty[quiz['difficulty']['level']]
                data.favorite = quiz['is_favor']
                data.acceptance = "%.1f%%" % (float(quiz['stat']['total_acs']) * 100 / float(quiz['stat']['total_submitted']))
                data.url = BASE_URL + "/problems/" + quiz['stat']['question__title_slug']
                data.submission_status = quiz['status']
                self.quizzes.append(data)
            return self.quizzes
        except (KeyError, AttributeError) as e:
            self.logger.error(e)

    @trace
    def get_user(self):
        if not self.auth.is_login:
            return
        query = """{
    user {
        username
        email
        isCurrentUserVerified
        isCurrentUserPremium
        __typename
    }
}"""
        extra_headers = {
            'Origin': BASE_URL,
            'Referer': BASE_URL,
            'X-CSRFToken': self.auth.cookies["csrftoken"],
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
        }

        new_headers = merge_two_dicts(extra_headers, headers)
        body = {
            'query': query,
            'operationName': None,
            'variables': {}
        }

        r = self.auth.retrieve(GRAPHQL_URL, headers=new_headers, method='POST', data=json.dumps(body))

        try:
            obj = json.loads(r.text)
            self.is_paid = obj["data"]["user"]["isCurrentUserPremium"]
            self.username = obj["data"]["user"]["username"]
            self.is_verified = obj["data"]["user"]["isCurrentUserVerified"]
        except Exception as e:
            self.logger.error(e)
            return None
