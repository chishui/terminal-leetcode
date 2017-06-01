import os
import json
import urwid
import logging
from .viewhelper import vim_key_map

class ResultView(urwid.Frame):
    '''
        Quiz Item Submission Result View
    '''
    def __init__(self, quiz, host_view, result, loop = None):
        self.quiz = quiz
        self.host_view = host_view
        self.result = result
        self.loop = loop
        self.logger = logging.getLogger(__name__)
        if result:
            if 'status_code' not in result:
                raise ValueError('Unknow result format: %s' % json.dumps(result))
            if result['status_code'] is 20:
                self.listbox = self.make_compile_error_view()
            elif result['status_code'] is 11:
                self.listbox = self.make_failed_view()
            elif result['status_code'] is 10:
                self.listbox = self.make_success_view()
            else:
                raise ValueError('Unknow status code: %d' % result['status_code'])
        else:
            raise ValueError('result shouldn\'t be None')

        #self.overlay = urwid.Overlay(
                    #urwid.LineBox(self.listbox), host_view, #urwid.SolidFill(),
                    #'center', ('relative', 95), 'middle', None)

        self.overlay = urwid.Overlay(urwid.LineBox(self.listbox), host_view,
            align='center', width=('relative', 95),
            valign='middle', height=('relative', 95),
            min_width=40, min_height=40)

        footer = urwid.Pile([urwid.Text('Press Esc to close this view.', align='center'),
            urwid.Divider()])
        urwid.Frame.__init__(self, self.overlay, footer=footer)

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
        return urwid.Padding(urwid.ListBox(urwid.SimpleListWalker(list_items)), left=2, right=2)

    def keypress(self, size, key):
        key = vim_key_map(key)
        if key is 'esc':
            self.destroy()
        else:
            return urwid.Frame.keypress(self, size, key)

    def show(self):
        if self.loop:
            self.loop.widget = self

    def destroy(self):
        if self.loop:
            self.loop.widget = self.host_view

