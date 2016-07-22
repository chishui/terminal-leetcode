
class QuizItem(object):
    def __init__(self, id, title, url, acceptance, difficulty, lock = False):
        self.id = id
        self.title = title
        self.url = url
        self.acceptance = acceptance
        self.difficulty = difficulty
        self.lock = lock
