import unittest
import mock
from leetcode.code import *

class TestCode(unittest.TestCase):

    @mock.patch('leetcode.code.os.path.exists')
    def test_unique_file_name(self, mock_exists):
        mock_exists.return_value = False
        self.assertEqual(unique_file_name(''), '')

        mock_exists.side_effect = [True, True, True, False]
        self.assertEqual(unique_file_name('hello'), 'hello-2')

        mock_exists.side_effect = [True, True, False]
        self.assertEqual(unique_file_name('hello.txt'), 'hello-1.txt')

        mock_exists.side_effect = [True, True, False]
        self.assertEqual(unique_file_name('hello.'), 'hello-1.')

    @mock.patch('leetcode.code.config')
    @mock.patch('leetcode.code.os.makedirs')
    def test_get_code_file_path(self, mock_makedirs, mock_config):
        mock_config.path = ''
        mock_config.ext = 'py'
        self.assertEqual(get_code_file_path(1), '~/leetcode/1.py')
        mock_makedirs.assert_called_once()
