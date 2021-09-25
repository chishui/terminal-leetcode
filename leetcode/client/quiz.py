import json
import logging
from bs4 import BeautifulSoup
from ..helper.config import config
from ..helper.trace import trace
from ..helper.common import BASE_URL, merge_two_dicts, GRAPHQL_URL, LANG_MAPPING, SUBMISSION_URL
from .auth import headers


class Quiz(object):
    def __init__(self, auth):
        self.id = None # question frontend id
        self.real_quiz_id = None # question id of backend
        self.title = None
        self.content = None
        self.sample_code = None
        self.locked = False
        self.difficulty = None
        self.acceptance = None
        self.submission_status = None
        self.favorite = None
        self.url = None
        self.discussion_url = None
        self.tags = []
        self.html_content = None
        self.auth = auth
        self.slug = None
        self.already_load = False
        self.logger = logging.getLogger(__name__)

    def load(self):
        if not self.auth.is_login or self.already_load:
            return False

        query = """query questionData($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        title
        titleSlug
        questionId
        questionFrontendId
        content
        difficulty
        stats
        companyTagStats
        topicTags {
            name
            slug
            __typename
        }
        similarQuestions
        codeSnippets {
            lang
            langSlug
            code
            __typename
        }
        solution {
            id
            canSeeDetail
            __typename
        }
        sampleTestCase
        enableTestMode
        metaData
        enableRunCode
        judgerAvailable
        __typename
    }
}"""
        extra_headers = {
            'Origin': BASE_URL,
            'Referer': self.url,
            'X-CSRFToken': self.auth.cookies['csrftoken'],
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
        }

        new_headers = merge_two_dicts(headers, extra_headers)
        body = {
            "query": query,
            "variables": {"titleSlug": self.slug},
            "operationName": "questionData"
        }
        r = self.auth.retrieve(GRAPHQL_URL, new_headers, "POST", json.dumps(body))
        try:
            obj = json.loads(r.text)
            self.html_content = obj["data"]["question"]["content"]
            content = obj["data"]["question"]["content"]
            bs = BeautifulSoup(content, "lxml")
            self.id = obj["data"]["question"]["questionFrontendId"]
            self.real_quiz_id = obj["data"]["question"]["questionId"]
            self.content = bs.get_text()
            self.content = self.content.replace(chr(13), '')
            self.sample_code = self._get_code_snippet(obj["data"]["question"]["codeSnippets"])
            self.tags = map(lambda x: x["name"], obj["data"]["question"]["topicTags"])
            self.already_load = True
            return True
        except Exception:
            self.logger.error("Fatal error in main loop", exc_info=True)
            return False

    def _get_code_snippet(self, snippets):
        for snippet in snippets:
            if snippet["lang"] == config.language:
                return snippet["code"]
        return ""

    @trace
    def submit(self, code):
        if not self.auth.is_login:
            return (False, "")
        body = {'question_id': self.real_quiz_id,
                'test_mode': False,
                'lang': LANG_MAPPING.get(config.language, 'cpp'),
                'judge_type': 'large',
                'typed_code': code}

        csrftoken = self.auth.cookies['csrftoken']
        extra_headers = {'Origin': BASE_URL,
                         'Referer': self.url + '/?tab=Description',
                         'DNT': '1',
                         'Content-Type': 'application/json;charset=UTF-8',
                         'Accept': 'application/json',
                         'X-CSRFToken': csrftoken,
                         'X-Requested-With': 'XMLHttpRequest'}

        newheaders = merge_two_dicts(headers, extra_headers)

        r = self.auth.retrieve(self.url + '/submit/', method='POST', data=json.dumps(body), headers=newheaders)
        if r.status_code != 200:
            return (False, 'Request failed!')
        text = r.text.encode('utf-8')
        try:
            data = json.loads(text)
        except Exception:
            return (False, text)

        if 'error' in data:
            return (False, data['error'])
        return (True, data['submission_id'])

    @trace
    def check_submission_result(self, submission_id):
        url = SUBMISSION_URL.format(id=submission_id)
        r = self.auth.retrieve(url)
        if r.status_code != 200:
            return (-100, 'Request failed!')
        text = r.text.encode('utf-8')
        data = json.loads(text)
        try:
            if data['state'] == 'PENDING':
                return (1,)
            elif data['state'] == 'STARTED':
                return (2,)
            elif data['state'] == 'SUCCESS':
                if 'run_success' in data:
                    if data['run_success']:
                        return (0, data)  # data['total_correct'], data['total_testcases'], data['status_runtime'])
                    else:
                        return (-1, data)  # data['compile_error'])
                else:
                    raise KeyError
        except KeyError:
            return (-2, 'Unknow error')
