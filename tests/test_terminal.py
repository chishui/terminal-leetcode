import unittest
import mock
from leetcode.terminal import Terminal
from leetcode.leetcode import Leetcode
from leetcode.views.loading import Toast
from leetcode.model import QuizItem

class TestTerminal(unittest.TestCase):
    def setUp(self):
        self.term = Terminal()

    @mock.patch.object(Terminal, 'retrieve_home_done')
    @mock.patch.object(Toast, 'show')
    @mock.patch.object(Leetcode, 'hard_retrieve_home')
    @mock.patch('leetcode.terminal.auth.login')
    @mock.patch('leetcode.terminal.auth.is_login')
    def test_run_retrieve_home(self, mock_is_login,
            mock_login,
            mock_retrieve_home,
            mock_toast_show,
            mock_done):
        mock_is_login.return_value = False
        mock_retrieve_home.return_value = None
        self.term.run_retrieve_home()
        mock_login.assert_called_once()
        mock_retrieve_home.assert_called_once()

        mock_is_login.return_value = True
        mock_done.mock_reset()
        mock_retrieve_home.return_value = [1]
        self.term.run_retrieve_home()
        mock_done.assert_called_once_with([1])

    @mock.patch.object(Terminal, 'retrieve_detail_done')
    @mock.patch.object(Toast, 'show')
    @mock.patch.object(Leetcode, 'retrieve_detail')
    def test_run_retrieve_detail(self, mock_retrieve_detail,
            mock_toast_show,
            mock_done):

        item = QuizItem({'id': 1,
                        'url': '/hello',
                        'title':'',
                        'acceptance':'',
                        'difficulty':'Easy',
                        'lock':True,
                        'pass': 'ac'})
        mock_retrieve_detail.return_value = None
        self.term.run_retrieve_detail(item)
        mock_done.assert_not_called()

        mock_retrieve_detail.return_value = ('a', 'b', 'c')
        self.term.run_retrieve_detail(item)
        mock_done.assert_called_once_with('a', 'b', 'c')


    @mock.patch.object(Toast, 'show')
    @mock.patch.object(Leetcode, 'submit_code')
    def test_run_retrieve_detail(self, mock_submit,
            mock_toast_show):
        mock_submit.return_value = None
