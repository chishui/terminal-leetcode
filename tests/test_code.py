import unittest
from pathlib import Path
from unittest.mock import patch
from leetcode.coding.code import *

class TestCode(unittest.TestCase):

    @patch('leetcode.coding.code.Path.exists')
    def test_unique_file_name(self, mock_exists):
        mock_exists.return_value = False
        self.assertEqual(unique_file_name(''), Path(''))

        mock_exists.side_effect = [True, True, True, False]
        self.assertEqual(unique_file_name('hello'), Path('hello-2'))

        mock_exists.side_effect = [True, True, False]
        self.assertEqual(unique_file_name('hello.txt'), Path('hello-1.txt'))

        mock_exists.side_effect = [True, True, False]
        self.assertEqual(unique_file_name('hello.'), Path('hello.-1'))

    @patch('leetcode.coding.code.config')
    @patch('leetcode.coding.code.Path.mkdir')
    @patch('leetcode.coding.code.Path.exists')
    def test_get_code_file_path(self, mock_exists, mock_makedirs, mock_config):
        mock_config.path = ''
        mock_config.ext = 'py'
        mock_exists.return_value = False
        self.assertEqual(get_code_file_path(1), Path.home().joinpath('leetcode/1.py'))
        mock_makedirs.assert_called_once()
