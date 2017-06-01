import unittest
import mock
from leetcode.views.result import ResultView

class TestResultView(unittest.TestCase):

    def test_exception(self):
        with self.assertRaises(ValueError):
            ResultView(None, None, None)
        with self.assertRaises(ValueError):
            ResultView(None, None, {})
        with self.assertRaises(ValueError):
            ResultView(None, None, {'status_code': 0})

    @mock.patch.object(ResultView, 'make_compile_error_view')
    def test_compile_error_view(self, mock_compile_error):
        view = ResultView(None, None, {'status_code': 20})
        mock_compile_error.assert_called_once()

    @mock.patch.object(ResultView, 'make_failed_view')
    def test_failed_view(self, mock_failed_view):
        view = ResultView(None, None, {'status_code': 11})
        mock_failed_view.assert_called_once()

    @mock.patch.object(ResultView, 'make_success_view')
    def test_success_view(self, mock_success_view):
        view = ResultView(None, None, {'status_code': 10})
        mock_success_view.assert_called_once()

    @mock.patch.object(ResultView, 'destroy')
    def test_press(self, mock_destroy):
        view = ResultView(None, None, {'status_code': 10, 'status_runtime': '6 ms'})
        view.keypress((20, 20), 'esc')
        mock_destroy.assert_called_once()
        mock_destroy.reset_mock()
        view.keypress((20, 20), 'e')
        mock_destroy.assert_not_called()
