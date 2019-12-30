import sys
import logging
from threading import Thread
import urwid
from .client.leetcode import Leetcode
from .views.home import HomeView
from .views.detail import DetailView
from .views.help import HelpView
from .views.loading import LoadingView, Toast
from .views.viewhelper import delay_refresh
from .views.result import ResultView
from .coding.code import get_code_file_path, get_code_for_submission

palette = [
    ('body', 'dark cyan', ''),
    ('focus', 'white', ''),
    ('head', 'white', 'dark gray'),
    ('lock', 'dark gray', ''),
    ('tag', 'white', 'light cyan', 'standout'),
    ('hometag', 'dark red', ''),
    ('accepted', 'dark green', '')
]


class Terminal(object):
    def __init__(self):
        self.home_view = None
        self.loop = None
        self.help_view = None
        self.quit_confirm_view = None
        self.submit_confirm_view = None
        self.view_stack = []
        self.detail_view = None
        self.search_view = None
        self.loading_view = None
        self.leetcode = Leetcode()
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
        if self.quit_confirm_view and self.current_view == self.quit_confirm_view:
            if key == 'y':
                raise urwid.ExitMainLoop()
            else:
                self.go_back()

        elif self.submit_confirm_view and self.current_view == self.submit_confirm_view:
            self.go_back()
            if key == 'y':
                self.send_code(self.detail_view.quiz)

        elif self.current_view == self.search_view:
            if key == 'enter':
                text = self.search_view.contents[1][0].original_widget.get_edit_text()
                self.home_view.handle_search(text)
                self.go_back()
            elif key == 'esc':
                self.go_back()

        elif key in ('q', 'Q'):
            self.goto_view(self.make_quit_confirmation())

        elif key == 's':
            if not self.is_home:
                self.goto_view(self.make_submit_confirmation())

        elif not self.is_home and (key == 'left' or key == 'h'):
            self.go_back()

        elif key == 'H':
            if not self.help_view:
                self.make_helpview()
            self.goto_view(self.help_view)

        elif key == 'R':
            if self.is_home:
                self.reload_list()

        elif key == 'f':
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
        self.leetcode.load()
        if self.leetcode.quizzes and len(self.leetcode.quizzes) > 0:
            self.home_view = self.make_listview(self.leetcode.quizzes)
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
        self.detail_view = DetailView(data, self.loop)
        return self.detail_view

    def make_listview(self, data):
        header = self.make_header()
        self.home_view = HomeView(data, header)
        return self.home_view

    def make_header(self):
        if self.leetcode.is_login:
            columns = [
                ('fixed', 15, urwid.Padding(urwid.AttrWrap(
                    urwid.Text('%s' % self.leetcode.username),
                    'head', ''))),
                urwid.AttrWrap(urwid.Text('You have solved %d / %d problems. ' % (
                    len(self.leetcode.solved), len(self.leetcode.quizzes))), 'head', ''),
                urwid.AttrWrap(urwid.Text(('Premium ' if self.leetcode.is_paid else 'Free '), align="right"), 'head', ''),
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

    def retrieve_home_done(self, quizzes):
        self.home_view = self.make_listview(quizzes)
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
        # self.leetcode.is_login = is_login()
        # if not self.leetcode.is_login:
        # self.leetcode.is_login = login()

        if self.loading_view:
            self.loading_view.set_text('Loading')

        self.leetcode.load()
        if self.leetcode.quizzes and len(self.leetcode.quizzes) > 0:
            self.retrieve_home_done(self.leetcode.quizzes)
        else:
            self.end_loading()
            toast = Toast('Request fail!', 10, self.current_view, self.loop)
            toast.show()
            self.logger.error('get quiz list fail')

    def run_retrieve_detail(self, quiz):
        ret = quiz.load()
        if ret:
            self.retrieve_detail_done(quiz)
        else:
            self.end_loading()
            toast = Toast('Request fail!', 10, self.current_view, self.loop)
            toast.show()
            self.logger.error('get detail %s fail', quiz.id)

    def run_send_code(self, quiz):
        filepath = get_code_file_path(quiz.id)
        if not filepath.exists():
            return
        code = get_code_for_submission(filepath)
        code = code.replace('\n', '\r\n')
        success, text_or_id = quiz.submit(code)
        if success:
            self.loading_view.set_text('Retrieving')
            code = 1
            while code > 0:
                r = quiz.check_submission_result(text_or_id)
                code = r[0]

            self.end_loading()
            if code < -1:
                toast = Toast('error: %s' % r[1], 10 + len(r[1]), self.current_view, self.loop)
                toast.show()
            else:
                try:
                    result = ResultView(quiz, self.detail_view, r[1], loop=self.loop)
                    result.show()
                except ValueError as e:
                    toast = Toast('error: %s' % e, 10 + len(str(e)), self.current_view, self.loop)
                    toast.show()
            delay_refresh(self.loop)
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
            self.logger.info('Keyboard interrupt')
        except Exception:
            self.logger.exception("Fatal error in main loop")
        finally:
            self.clear_thread()
            sys.exit()

    def clear_thread(self):
        if self.loading_view:
            self.loading_view.end()
        if self.t and self.t.is_alive():
            self.t.join()
