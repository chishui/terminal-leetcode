import os
import ConfigParser

HOME = os.path.expanduser('~')
CONFIG_FOLDER = os.path.join(HOME, '.config', 'leetcode')
CONFIG_FILE = os.path.join(CONFIG_FOLDER, 'config.cfg')

class Config(object):
    '''
    Config is a class to get user's configuration from leetcode.cfg
    config.cfg is located ~/.config/leetcdoe/config.cfg
    keys are:
        username
        password
        language
    '''
    def __init__(self):
        self.parser = ConfigParser.SafeConfigParser({'username' : '','password' : '',
            'language' : 'C++'})
        self.username = None
        self.password = None
        self.language = 'C++'

    def load(self):
        if not os.path.exists(CONFIG_FILE):
            return False

        self.parser.read(CONFIG_FILE)
        if 'leetcode' not in self.parser.sections():
            return False

        self.username = self.parser.get('leetcode', 'username')
        self.password = self.parser.get('leetcode', 'password')
        self.language = self.parser.get('leetcode', 'language')
        return True
