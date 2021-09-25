import json
from collections import OrderedDict
from .leetcode import Leetcode
from ..helper.trace import trace
from ..coding.code import get_code_file_path, get_code_for_submission


class Process(object):
    def __init__(self):
        self.leetcode = Leetcode()

    @trace
    def get_code_from_quiz_id(self, id):
        filepath = get_code_file_path(id)
        if not filepath.exists():
            return None
        code = get_code_for_submission(filepath)
        code = code.replace('\n', '\r\n')
        return code

    @trace
    def _submit_result_prettify(self, result):
        prettified = OrderedDict()
        if 'status_code' not in result:
            prettified['status'] = 'Unknow result format: %s' % json.dumps(result)
        if result['status_code'] == 20:
            prettified['status'] = 'Compile error'
            prettified['Your input'] = ''
            prettified['Your answer'] = result['compile_error']
            prettified['Expected answer'] = 'Unknown error'
        elif result['status_code'] == 10:
            prettified['status'] = 'Accepted'
            prettified['Run time'] = result['status_runtime']
        elif result['status_code'] == 11:
            prettified['status'] = 'Wrong answer'
            s = result['compare_result']
            prettified['Passed test cases'] = '%d/%d' % (s.count('1'), len(s))
            prettified['Your input'] = result['input']
            prettified['Your answer'] = result['code_output']
            prettified['Expected answer'] = result['expected_output']
        elif result['status_code'] == 12:  # memeory limit exceeded
            prettified['status'] = 'Memory Limit Exceeded'
        elif result['status_code'] == 13:  # output limit exceeded
            prettified['status'] = 'Output Limit Exceeded'
        elif result['status_code'] == 14:  # timeout
            prettified['status'] = 'Time Limit Exceeded'
        elif result['status_code'] == 15:
            prettified['status'] = 'Runtime error'
            prettified['Runtime error message'] = result['runtime_error']
            prettified['Last input'] = result['last_testcase']
        else:
            prettified['status'] = 'Unknown status'
        return prettified

    @trace
    def submit(self, id):
        self.leetcode.load()
        quiz = None
        for q in self.leetcode.quizzes:
            if q.id == id:
                quiz = q
                break
        if not quiz:
            return (False, None)
        else:
            quiz.load()

        code = self.get_code_from_quiz_id(id)
        success, text_or_id = quiz.submit(code)
        if success:
            code = 1
            while code > 0:
                r = quiz.check_submission_result(text_or_id)
                code = r[0]

            if code < -1:
                return (False, r[1])
            else:
                return (True, self._submit_result_prettify(r[1]))
        else:
            return (False, 'send data failed!')
