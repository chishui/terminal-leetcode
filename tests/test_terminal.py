import unittest
import mock
from leetcode.terminal import Terminal
from leetcode.leetcode import Leetcode, Quiz
from leetcode.views.loading import Toast

class TestTerminal(unittest.TestCase):
    def setUp(self):
        self.term = Terminal()

    @mock.patch.object(Terminal, 'retrieve_home_done')
    @mock.patch.object(Toast, 'show')
    @mock.patch.object(Leetcode, 'load')
    @mock.patch('leetcode.terminal.auth.login')
    @mock.patch('leetcode.terminal.auth.is_login')
    def test_run_retrieve_home(self, mock_is_login,
            mock_login,
            mock_load,
            mock_toast_show,
            mock_done):
        mock_is_login.return_value = False
        mock_load.return_value = None
        self.term.run_retrieve_home()
        mock_login.assert_called_once()
        mock_load.assert_called_once()

        #mock_is_login.return_value = True
        #mock_done.mock_reset()
        #mock_load.return_value = [1]
        #mock_quizzes.return_value.quizzes = [1]
        #self.term.run_retrieve_home()
        #mock_done.assert_called_once_with([1])

    @mock.patch.object(Terminal, 'retrieve_detail_done')
    @mock.patch.object(Toast, 'show')
    @mock.patch.object(Quiz, 'load')
    def test_run_retrieve_detail(self, mock_retrieve_detail,
            mock_toast_show,
            mock_done):

        item = Quiz()
        item.id = 1
        item.url = 'http://hello.com'
        item.title = ''
        item.acceptance = ''
        item.difficulty = 'Easy'
        item.locked = True
        item.submission_status = 'ac'

        mock_retrieve_detail.return_value = False
        self.term.run_retrieve_detail(item)
        mock_done.assert_not_called()

        mock_retrieve_detail.return_value = True
        self.term.run_retrieve_detail(item)
        mock_done.assert_called_once_with(item)


    #@mock.patch.object(Toast, 'show')
    #@mock.patch.object(Leetcode, 'submit_code')
    #def test_run_retrieve_detail(self, mock_submit,
            #mock_toast_show):
        #mock_submit.return_value = None
