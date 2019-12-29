import os
import configparser
from pathlib import Path

HOME = Path.home()
CONFIG_FOLDER = HOME.joinpath('.config', 'leetcode')
CONFIG_FILE = CONFIG_FOLDER.joinpath('config.cfg')
TAG_FILE = CONFIG_FOLDER.joinpath('tag.json')

class Config(object):
    '''
    Config is a class to get user's configuration from leetcode.cfg
    config.cfg is located ~/.config/leetcdoe/config.cfg
    keys are:
        username
        password
        language
        ext # code file extension
        path # code path
    '''
    def __init__(self):
        self.parser = configparser.ConfigParser({'username' : '', 'password' : '',
                                                     'language' : 'C++', 'ext': '',
                                                     'path' : '', 'keep_quiz_detail': 'false',
                                                     'tmux_support': 'false'})
        self.username = None
        self.password = None
        self.language = 'C++'
        self.ext = ''
        self.path = None
        self.keep_quiz_detail = False
        self.tmux_support = False

    def load(self):
        if not CONFIG_FILE.exists():
            return True

        self.parser.read(CONFIG_FILE)
        if 'leetcode' not in self.parser.sections():
            return False

        self.username = self.parser.get('leetcode', 'username')
        self.password = self.parser.get('leetcode', 'password')
        self.language = self.parser.get('leetcode', 'language')
        self.ext = self.parser.get('leetcode', 'ext')
        self.path = self.parser.get('leetcode', 'path')
        self.path = os.path.expanduser(self.path)
        self.keep_quiz_detail = self.parser.getboolean('leetcode', 'keep_quiz_detail')
        self.tmux_support = self.parser.getboolean('leetcode', 'tmux_support')
        return True

config = Config()
