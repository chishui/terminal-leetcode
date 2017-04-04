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

