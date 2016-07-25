
class QuizItem(object):
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.url = data['url']
        self.acceptance = data['acceptance']
        self.difficulty = data['difficulty']
        self.lock = data['lock']
        self.pass_status = data['pass']#'None', 'ac', 'notac'
        self.sample_code = None

