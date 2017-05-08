import sys
import time
import logging
from threading import Thread
import urwid
from .leetcode import Leetcode
from views.home import HomeView
from views.detail import DetailView
from views.help import HelpView
from views.loading import *
from views.viewhelper import *
from .config import config
import auth
from .model import DetailData

palette = [
    ('body', 'dark cyan', ''),
    ('focus', 'white', ''),
    ('head', 'white', 'dark gray'),
    ('lock', 'dark gray', ''),
    ('tag', 'white', 'light cyan', 'standout'),
    ('hometag', 'dark red', '')
    ]

STATUS_ACCEPTED = 10
STATUS_WRONG_ANSWER = 11
STATUS_RUNTIME_ERROR = 15
STATUS_COMPILATION_ERROR = 20

class Terminal(object):
    def __init__(self):
        self.home_view = None
        self.loop = None
        self.leetcode = Leetcode()
        self.help_view = None
        self.quit_confirm_view = None
        self.submit_confirm_view = None
        self.view_stack = []
        self.detail_view = None
        self.search_view = None
        self.result_view = None
        self.loading_view = None
        self.logger = logging.getLogger(__name__)

    @property
    def current_view(self):
        return None if not len(self.view_stack) else self.view_stack[-1]

    @property
    def is_home(self):
        return len(self.view_stack) == 1

    def goto_view(self, view):
        self.loop.widget = view
        self.view_stack.append(view)

    def go_back(self):
        self.view_stack.pop()
        self.loop.widget = self.current_view

    def keystroke(self, key):
        # on result view, return to previous view if not scrolling
        if self.result_view and self.current_view == self.result_view:
            key = vim_key_map(key)
            if key not in ['up', 'down', 'left']:
                self.go_back()

        if self.quit_confirm_view and self.current_view == self.quit_confirm_view:
            if key is 'y':
                raise urwid.ExitMainLoop()
            else:
                self.go_back()

        elif self.submit_confirm_view and self.current_view == self.submit_confirm_view:
            self.go_back()
            if key is 'y':
                self.send_code(self.detail_view.data)

        elif self.current_view == self.search_view:
            if key is 'enter':
                text = self.search_view.contents[1][0].original_widget.get_edit_text()
                self.home_view.handle_search(text)
                self.go_back()
            elif key is 'esc':
                self.go_back()

        elif key in ('q', 'Q'):
            self.goto_view(self.make_quit_confirmation())

        elif key is 's':
            self.goto_view(self.make_submit_confirmation())

        elif not self.is_home and (key is 'left' or key is 'h'):
            self.go_back()

        elif key is 'H':
            if not self.help_view:
                self.make_helpview()
            self.goto_view(self.help_view)

        elif key is 'R':
            if self.is_home:
                self.reload_list()

        elif key is 'f':
            if self.is_home:
                self.enter_search()

        elif key in ('enter', 'right'):
            if self.is_home and self.home_view.is_current_item_enterable():
                self.enter_detail(self.home_view.get_current_item_data())

        else:
            return key

    def enter_search(self):
        self.make_search_view()
        self.goto_view(self.search_view)

    def enter_detail(self, data):
        self.show_loading('Loading Quiz', 17, self.current_view)
        self.t = Thread(target=self.run_retrieve_detail, args=(data,))
        self.t.start()

    def reload_list(self):
        '''Press R in home view to retrieve quiz list'''
        items = self.leetcode.hard_retrieve_home()
        if items:
            self.home_view = self.make_listview(items)
            self.view_stack = []
            self.goto_view(self.home_view)

    def make_quit_confirmation(self):
        text = urwid.AttrMap(urwid.Text('Do you really want to quit ? (y/n)'), 'body')
        self.quit_confirm_view = urwid.Overlay(text, self.current_view, 'left',
                                               ('relative', 100), 'bottom', None)
        return self.quit_confirm_view

    def make_submit_confirmation(self):
        text = urwid.AttrMap(urwid.Text('Do you want to submit your code ? (y/n)'), 'body')
        self.submit_confirm_view = urwid.Overlay(text, self.current_view, 'left',
                                               ('relative', 100), 'bottom', None)
        return self.submit_confirm_view

    def make_search_view(self):
        text = urwid.AttrMap(urwid.Edit('Search by id: ', ''), 'body')
        self.search_view = urwid.Overlay(text, self.current_view, 'left',
                                               ('relative', 100), 'bottom', None)
        return self.search_view

    def make_detailview(self, data):
        self.detail_view = DetailView(data, self.leetcode, self.loop)
        return self.detail_view

    def make_result_view(self, result):
        msg = ['=================']
        msg.append('Submission Result')
        msg.append('=================')

        if result['status_code'] == STATUS_ACCEPTED:
            msg.append('Result: Accepted')
            msg.append('Runtime: %s' % (result['status_runtime']))
            msg.append('Testcase: %d / %d' % (result['total_correct'],
                                              result['total_testcases']))
        elif result['status_code'] == STATUS_RUNTIME_ERROR:
            msg.append('Result: Runtime Error')
            msg.append('Error msg: %s' % (result['runtime_error']))
            msg.append('Last testcase: %s' % (result.get('last_testcase', '')))
        elif result['status_code'] == STATUS_WRONG_ANSWER:
            msg.append('Result: Wrong Answer')
            msg.append('Testcase: %d / %d' % (result['total_correct'],
                                              result['total_testcases']))
            msg.append('Input: %s' % (result['input']))
            msg.append('Output: %s' % (result['code_output']))
            msg.append('Expected: %s' % (result['expected_output']))
            if result.get('std_output', '') != '':
                msg.append('Stdout: %s' % (result['std_output']))
        elif result['status_code'] == STATUS_COMPILATION_ERROR:
            msg.append('Result: Compile Error')
            msg.append('Error: %s' % (result.get('compile_error', '')))
        else:
            msg.append('Status unknown: %d' % (result['status_code']))

        text = urwid.AttrMap(urwid.Text('\n'.join(msg)), 'body')
        self.result_view = urwid.Overlay(text, self.current_view, 'left',
                                         ('relative', 100), 'bottom', None)
        return self.result_view

    def make_listview(self, data):
        header = self.make_header()
        self.home_view = HomeView(data, header)
        return self.home_view

    def make_header(self):
        if self.leetcode.is_login:
            columns = [
                ('fixed', 15, urwid.Padding(urwid.AttrWrap(
                    urwid.Text('%s' % config.username),
                    'head', ''))),
                urwid.AttrWrap(urwid.Text('You have solved %d / %d problems. ' %
                    (len(self.leetcode.solved), len(self.leetcode.items))), 'head', ''),
            ]
            return urwid.Columns(columns)
        else:
            text = urwid.AttrWrap(urwid.Text('Not login'), 'head')
        return text

    def make_helpview(self):
        self.help_view = HelpView()
        return self.help_view

    def show_loading(self, text, width, host_view=urwid.SolidFill()):
        self.loading_view = LoadingView(text, width, host_view, self.loop)
        self.loop.widget = self.loading_view
        self.loading_view.start()

    def end_loading(self):
        if self.loading_view:
            self.loading_view.end()
            self.loading_view = None

    def retrieve_home_done(self, data):
        self.home_view = self.make_listview(data)
        self.view_stack = []
        self.goto_view(self.home_view)
        self.end_loading()
        delay_refresh(self.loop)

    def retrieve_detail_done(self, data):
        data.id = self.home_view.listbox.get_focus()[0].data.id
        data.url = self.home_view.listbox.get_focus()[0].data.url
        self.goto_view(self.make_detailview(data))
        self.end_loading()
        delay_refresh(self.loop)

    def run_retrieve_home(self):
        self.leetcode.is_login = auth.is_login()
        if not self.leetcode.is_login:
            self.leetcode.is_login = auth.login()

        if self.loading_view:
            self.loading_view.set_text('Loading')
        data = self.leetcode.hard_retrieve_home()
        if data:
            self.retrieve_home_done(data)
        else:
            self.end_loading()
            toast = Toast('Request fail!', 10, self.current_view, self.loop)
            toast.show()
            self.logger.error('get quiz list fail')

    def run_retrieve_detail(self, data):
        ret = self.leetcode.retrieve_detail(data)
        if ret:
            self.retrieve_detail_done(ret)
        else:
            self.end_loading()
            toast = Toast('Request fail!', 10, self.current_view, self.loop)
            toast.show()
            self.logger.error('get detail %s fail', data.id)

    def run_send_code(self, data):
        success, text_or_id = self.leetcode.submit_code(data)
        if success:
            self.loading_view.set_text('Retrieving')
            code = 1
            while code > 0:
                r = self.leetcode.check_submission_result(text_or_id)
                code = r[0]

            self.end_loading()
            result = r[1]
            self.goto_view(self.make_result_view(result))
        else:
            self.end_loading()
            toast = Toast('error: %s' % text_or_id, 10 + len(text_or_id), self.current_view, self.loop)
            toast.show()
            self.logger.error('send data fail')

    def send_code(self, data):
        self.show_loading('Sending code', 17, self.current_view)
        self.t = Thread(target=self.run_send_code, args=(data,))
        self.t.start()

    def run(self):
        self.loop = urwid.MainLoop(None, palette, unhandled_input=self.keystroke)
        self.show_loading('Log In', 12)
        self.t = Thread(target=self.run_retrieve_home)
        self.t.start()
        try:
            self.loop.run()
        except KeyboardInterrupt:
            sys.exit()
        finally:
            self.logger.exception("Fatal error in main loop")
            self.logger.info("clear thread")
            self.clear_thread()

    def clear_thread(self):
        if self.loading_view:
            self.loading_view.end()
        if self.t and self.t.is_alive():
            t.join()

