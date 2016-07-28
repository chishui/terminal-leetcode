import urwid
from .leetcode import Leetcode
from .views import HomeView, DetailView, HelpView

palette = [
    ('body', 'dark cyan', ''),
    ('focus', 'white', ''),
    ('head', 'white', 'dark gray'),
    ('lock', 'dark gray', '')
    ]

class Terminal(object):
    def __init__(self):
        self.home_view = None
        self.loop = None
        self.leetcode = Leetcode()
        self.help_view = None
        self.quit_confirm_view = None
        self.view_stack = []
        self.detail_view = None
        self.search_view = None

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
            if key is 'y':
                raise urwid.ExitMainLoop()
            else:
                self.go_back()

        elif self.current_view == self.search_view and key is 'enter':
            text = self.search_view.contents[1][0].original_widget.get_edit_text()
            for i, item in enumerate(self.home_view.listbox.contents()):
                if item[0].data.id == text:
                    self.home_view.listbox.focus_position = i
                    break
            self.go_back()

        elif key in ('q', 'Q'):
            self.goto_view(self.make_quit_confirmation())

        elif key is 'R':
            items = self.leetcode.hard_retrieve_home()
            self.home_view = self.make_listview(items)
            self.view_stack = []
            self.goto_view(self.home_view)

        elif self.is_home and (key is 'l' or key is 'enter' or key is 'right'):
            if  self.home_view.listbox.get_focus()[0].selectable():
                if self.detail_view and self.detail_view.title == self.home_view.listbox.get_focus()[0].data.title:
                    self.goto_view(self.detail_view)
                else:
                    title, body, code = self.leetcode.retrieve_detail(self.home_view.listbox.get_focus()[0].data)
                    self.goto_view(self.make_detailview(title, body, code))

        elif not self.is_home and (key is 'left' or key is 'h'):
            self.go_back()

        elif key is 'H':
            if not self.help_view:
                self.make_helpview()
            self.goto_view(self.help_view)

        elif self.is_home and key is 'f':
            self.make_search_view()
            self.goto_view(self.search_view)

        else:
            return key

    def make_quit_confirmation(self):
        text = urwid.AttrMap(urwid.Text('Do you really want to quit ? (y/n)'), 'body')
        self.quit_confirm_view = urwid.Overlay(text, self.current_view, 'left',
                                               ('relative', 100), 'bottom', None)
        return self.quit_confirm_view

    def make_search_view(self):
        text = urwid.AttrMap(urwid.Edit('Search by id: ', ''), 'body')
        self.search_view = urwid.Overlay(text, self.current_view, 'left',
                                               ('relative', 100), 'bottom', None)
        return self.search_view

    def make_detailview(self, title, body, code):
        quizid = self.home_view.listbox.get_focus()[0].data.id
        self.detail_view = DetailView(title, body, code, quizid, self.leetcode.config)
        return self.detail_view

    def make_listview(self, data):
        header = self.make_header()
        self.home_view = HomeView(data, header)
        return self.home_view

    def make_header(self):
        if self.leetcode.is_login:
            columns = [
                ('fixed', 15, urwid.Padding(urwid.AttrWrap(
                    urwid.Text('%s' % self.leetcode.config.username),
                    'head', ''), left=2)),
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

    def run(self):
        self.leetcode.login()
        data = self.leetcode.hard_retrieve_home()
        self.home_view = self.make_listview(data)
        self.loop = urwid.MainLoop(self.home_view, palette, unhandled_input=self.keystroke)
        self.view_stack.append(self.home_view)
        self.loop.run()


if __name__ == '__main__':
    term = Terminal()
    term.run()
