import unittest
from unittest.mock import patch
from leetcode.editor import edit

class TestEditor(unittest.TestCase):
    @patch('leetcode.editor.os.chdir')
    @patch('leetcode.editor.subprocess.call')
    @patch('leetcode.editor.os.environ.get')
    def test_edit(self, mock_get, mock_call, mock_chdir):
        mock_get.return_value = ''
        edit('', None)
        mock_call.assert_not_called()

        mock_get.return_value = 'sublime'
        edit('file', None)
        mock_call.assert_called_once_with('subl file', shell=True)

        mock_get.return_value = 'vim'
        mock_call.reset_mock()
        with patch('leetcode.editor.delay_refresh_detail') as mock_delay:
            edit('file', None)
            mock_call.assert_called_once_with('vim file', shell=True)
            mock_delay.assert_called_once()

