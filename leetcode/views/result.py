import json
import urwid
import logging
from .viewhelper import vim_key_map


class ResultView(urwid.Frame):
    '''
        Quiz Item Submission Result View
    '''
    def __init__(self, quiz, host_view, result, loop=None):
        self.quiz = quiz
        self.host_view = host_view
        self.result = result
        self.loop = loop
        self.logger = logging.getLogger(__name__)
        if result:
            if 'status_code' not in result:
                raise ValueError('Unknow result format: %s' % json.dumps(result))
            if result['status_code'] == 20:
                self.listbox = self.make_compile_error_view()
            elif result['status_code'] == 10:
                self.listbox = self.make_success_view()
            elif result['status_code'] == 11:
                self.listbox = self.make_failed_view()
            elif result['status_code'] == 12:  # memeory limit exceeded
                self.listbox = self.make_unified_error_view("Memory Limit Exceeded")
            elif result['status_code'] == 13:  # output limit exceeded
                self.listbox = self.make_unified_error_view("Output Limit Exceeded")
            elif result['status_code'] == 14:  # timeout
                self.listbox = self.make_unified_error_view("Time Limit Exceeded")
            elif result['status_code'] == 15:
                self.listbox = self.make_runtime_error_view()
            else:
                raise ValueError('Unknow status code: %d' % result['status_code'])
        else:
            raise ValueError('result shouldn\'t be None')

        self.overlay = urwid.Overlay(
            urwid.LineBox(self.listbox), host_view,
            align='center', width=('relative', 95),
            valign='middle', height=('relative', 95),
            min_width=40, min_height=40)

        footer = urwid.Pile([urwid.Text('Press Esc to close this view.', align='center'), urwid.Divider()])
        urwid.Frame.__init__(self, self.overlay, footer=footer)

    def _append_stdout_if_non_empty(self, list_items):
        std_output = self.result.get('std_output', '')
        if len(std_output) > 0:
            blank = urwid.Divider()
            stdout_header = urwid.Text('Stdout:')
            if len(std_output) > 100:
                std_output = '%s...%s\n(output trimmed due to its length)' %\
                    (std_output[:90], std_output[-10:])
            stdout = urwid.Text(std_output)
            list_items.extend([blank, stdout_header, stdout])

    def make_success_view(self):
        blank = urwid.Divider()
        status_header = urwid.AttrWrap(urwid.Text('Run Code Status: '), 'body')
        status = urwid.AttrWrap(urwid.Text('Accepted'), 'accepted')
        columns = urwid.Columns([(20, status_header), (20, status)])
        runtime = urwid.Text('Run time: %s' % self.result['status_runtime'])
        result_header = urwid.Text('--- Run Code Result: ---', align='center')
        list_items = [
            result_header,
            blank, columns,
            blank, runtime
        ]
        self._append_stdout_if_non_empty(list_items)
        return urwid.Padding(urwid.ListBox(urwid.SimpleListWalker(list_items)), left=2, right=2)

    def make_failed_view(self):
        blank = urwid.Divider()
        status_header = urwid.AttrWrap(urwid.Text('Run Code Status: '), 'body')
        status = urwid.AttrWrap(urwid.Text('Wrong Answer'), 'hometag')
        columns = urwid.Columns([(17, status_header), (20, status)])
        result_header = urwid.Text('--- Run Code Result: ---', align='center')
        passed_header = urwid.Text('Passed test cases:')
        s = self.result['compare_result']
        passed = urwid.Text('%d/%d' % (s.count('1'), len(s)))
        your_input_header = urwid.Text('Your input:')
        your_input = urwid.Text(self.result['input'])
        your_answer_header = urwid.Text('Your answer:')
        your_answer = urwid.Text(self.result['code_output'])
        expected_answer_header = urwid.Text('Expected answer:')
        expected_answer = urwid.Text(self.result['expected_output'])
        list_items = [
            result_header,
            blank, columns,
            blank, passed_header, passed,
            blank, your_input_header, your_input,
            blank, your_answer_header, your_answer,
            blank, expected_answer_header, expected_answer
        ]
        self._append_stdout_if_non_empty(list_items)
        return urwid.Padding(urwid.ListBox(urwid.SimpleListWalker(list_items)), left=2, right=2)

    def make_compile_error_view(self):
        blank = urwid.Divider()
        status_header = urwid.AttrWrap(urwid.Text('Run Code Status: '), 'body')
        status = urwid.AttrWrap(urwid.Text('Compile Error'), 'hometag')
        columns = urwid.Columns([(17, status_header), (20, status)])
        column_wrap = urwid.WidgetWrap(columns)
        result_header = urwid.Text('--- Run Code Result: ---', align='center')
        your_input_header = urwid.Text('Your input:')
        your_input = urwid.Text('')
        your_answer_header = urwid.Text('Your answer:')
        your_answer = urwid.Text(self.result['compile_error'])
        expected_answer_header = urwid.Text('Expected answer:')
        expected_answer = urwid.Text('Unkown Error')
        list_items = [
            result_header,
            blank, column_wrap,
            blank, your_input_header, your_input,
            blank, your_answer_header, your_answer,
            blank, expected_answer_header, expected_answer
        ]
        self._append_stdout_if_non_empty(list_items)
        return urwid.Padding(urwid.ListBox(urwid.SimpleListWalker(list_items)), left=2, right=2)

    def make_runtime_error_view(self):
        blank = urwid.Divider()
        status_header = urwid.AttrWrap(urwid.Text('Run Code Status: '), 'body')
        status = urwid.AttrWrap(urwid.Text('Runtime Error'), 'hometag')
        columns = urwid.Columns([(17, status_header), (20, status)])
        column_wrap = urwid.WidgetWrap(columns)
        result_header = urwid.Text('--- Run Code Result: ---', align='center')
        error_header = urwid.Text('Runtime Error Message:')
        error_message = urwid.Text(self.result['runtime_error'])
        your_input_header = urwid.Text('Last input:')
        your_input = urwid.Text(self.result['last_testcase'])
        list_items = [
            result_header,
            blank, column_wrap,
            blank, error_header, error_message,
            blank, your_input_header, your_input,
        ]
        self._append_stdout_if_non_empty(list_items)
        return urwid.Padding(urwid.ListBox(urwid.SimpleListWalker(list_items)), left=2, right=2)

    def make_unified_error_view(self, error_title):
        blank = urwid.Divider()
        status_header = urwid.AttrWrap(urwid.Text('Run Code Status: '), 'body')
        status = urwid.AttrWrap(urwid.Text(error_title), 'hometag')
        columns = urwid.Columns([(17, status_header), (30, status)])
        column_wrap = urwid.WidgetWrap(columns)
        if 'last_testcase' in self.result:
            result_header = urwid.Text('--- Run Code Result: ---', align='center')
            your_input_header = urwid.Text('Last executed input:')
            your_input = urwid.Text(self.result['last_testcase'])
            list_items = [
                result_header,
                blank, column_wrap,
                blank, your_input_header, your_input,
            ]
        else:
            list_items = [
                result_header,
                blank, column_wrap,
            ]
        self._append_stdout_if_non_empty(list_items)
        return urwid.Padding(urwid.ListBox(urwid.SimpleListWalker(list_items)), left=2, right=2)

    def keypress(self, size, key):
        key = vim_key_map(key)
        if key == 'esc':
            self.destroy()
        else:
            return urwid.Frame.keypress(self, size, key)

    def show(self):
        if self.loop:
            self.loop.widget = self

    def destroy(self):
        if self.loop:
            self.loop.widget = self.host_view
