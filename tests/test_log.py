import unittest
import os
from unittest import mock
import json
from leetcode.helper.log import *

data = '''
{
    "version": 1,
    "disable_existing_loggers": false,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        }
    },
    "handlers": {
        "default": {
            "level":"INFO",
            "class":"logging.StreamHandler"
        }
    },
    "loggers": {
        "": {
            "level": "INFO",
            "propagate": true
        }
    }
}
'''

class TestLog(unittest.TestCase) :

    @mock.patch('leetcode.helper.log.read_json_data')
    @mock.patch('leetcode.helper.log.os.path.exists')
    def test_init_logger(self, mock_path, mock_read_data):
        mock_path.return_value = False
        init_logger()

        mock_read_data.return_value = json.loads(data)
        mock_path.return_value = True
        init_logger()

    @mock.patch('builtins.open')
    def test_read_json_data(self, mock_open):
        mock_open.return_value.__enter__.return_value.read.return_value = data
        self.assertEqual(read_json_data(json_file), json.loads(data))

if __name__== "__main__":
    unittest.main()

