import unittest
import mock
from mock import mock_open
from leetcode.config import *
import io

class TestConfig(unittest.TestCase):

    @mock.patch('leetcode.config.os.path.exists')
    def test_config_missing(self, mock_exists):
        mock_exists.return_value = False
        self.assertFalse(Config().load())

    @mock.patch('leetcode.config.os.path.exists')
    @mock.patch('__builtin__.open')
    def test_config_item_missing(self, mock_open, mock_exists):
        file_content = "[leetcode]\n"\
                       "language=C++\n"\
                       "ext=cpp"
        mock_exists.return_value = True
        mock_open.return_value = io.BytesIO(file_content)
        self.assertTrue(Config().load())

    @mock.patch('leetcode.config.os.path.exists')
    @mock.patch('__builtin__.open')
    def test_config_tag_missing(self, mock_open, mock_exists):
        file_content = "[error]\n"\
                       "language=C++\n"\
                       "ext=cpp"
        mock_exists.return_value = True
        mock_open.return_value = io.BytesIO(file_content)
        self.assertFalse(Config().load())

    @mock.patch('leetcode.config.os.path.exists')
    @mock.patch('__builtin__.open')
    def test_config_right(self, mock_open, mock_exists):
        file_content = "[leetcode]\n"\
                        "username=test\n"\
                        "password=lalala\n"\
                        "language=python\n"\
                        "ext=py\n"\
                        "path=~/test\n"

        mock_exists.return_value = True
        mock_open.return_value = io.BytesIO(file_content)

        conf = Config()
        self.assertTrue(conf.load())
        self.assertEqual(conf.path, os.path.join(os.environ['HOME'], 'test'))
        self.assertEqual(conf.username, 'test')
        self.assertEqual(conf.password, 'lalala')
        self.assertEqual(conf.language, 'python')
        self.assertEqual(conf.ext, 'py')
