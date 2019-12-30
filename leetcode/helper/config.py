import os
import configparser
from pathlib import Path

HOME = Path.home()
CONFIG_FOLDER = HOME.joinpath('.config', 'leetcode')
CONFIG_FILE = CONFIG_FOLDER.joinpath('config.cfg')
TAG_FILE = CONFIG_FOLDER.joinpath('tag.json')
SECTION = 'leetcode'


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
        self.parser = configparser.ConfigParser({
            'username': '',
            'password': '',
            'language': 'C++',
            'ext': '',
            'path': '',
            'keep_quiz_detail': 'false',
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
        if SECTION not in self.parser.sections():
            return False

        self.username = self.parser.get(SECTION, 'username')
        self.password = self.parser.get(SECTION, 'password')
        self.language = self.parser.get(SECTION, 'language')
        self.ext = self.parser.get(SECTION, 'ext')
        self.path = self.parser.get(SECTION, 'path')
        self.path = os.path.expanduser(self.path)
        self.keep_quiz_detail = self.parser.getboolean(SECTION, 'keep_quiz_detail')
        self.tmux_support = self.parser.getboolean(SECTION, 'tmux_support')
        return True

    def write(self, key, value):
        self.load()
        self.parser.set(SECTION, key, value)
        with open(CONFIG_FILE, 'w') as configfile:
            self.parser.write(configfile)


config = Config()
