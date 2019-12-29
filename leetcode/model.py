from threading import Lock


class EasyLock(object):
    def __init__(self):
        self.lock = Lock()

    def __enter__(self):
        self.lock.acquire()
        return self.lock

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()
