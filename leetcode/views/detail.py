import webbrowser
import urwid
import logging
from .viewhelper import vim_key_map
from ..coding.code import edit_code
from ..helper.common import BASE_URL
from ..coding.editor import edit
from ..helper.trace import trace


class DetailView(urwid.Frame):
    '''
        Quiz Item Detail View
    '''
    def __init__(self, quiz, loop=None):
        self.quiz = quiz
        self.loop = loop
        self.logger = logging.getLogger(__name__)
        blank = urwid.Divider()
        view_title = urwid.AttrWrap(urwid.Text(self.quiz.title), 'body')
        view_text = self.make_body_widgets()
        view_code_title = urwid.Text('\n --- Sample Code ---\n')
        view_code = urwid.Text(self.quiz.sample_code)
        listitems = [blank, view_title, blank] + view_text + \
                    [blank, view_code_title, blank, view_code, blank]
        self.listbox = urwid.ListBox(urwid.SimpleListWalker(listitems))
        urwid.Frame.__init__(self, self.listbox)

    def make_body_widgets(self):
        text_widgets = []

        for line in self.quiz.content.split('\n'):
            text_widgets.append(urwid.Text(line))

        text_widgets.append(urwid.Divider())

        for tag in self.quiz.tags:
            text_widgets.append(urwid.Text(('tag', tag)))

        return text_widgets

    @trace
    def keypress(self, size, key):
        key = vim_key_map(key)
        ignore_key = ('l', 'right', 'enter')
        if key in ignore_key:
            pass
        # edit sample code
        if key == 'e':
            self.edit_code(False)
        # edit new sample code
        elif key == 'n':
            self.edit_code(True)
        # open discussion page from default browser
        elif key == 'd':
            url = self.get_discussion_url()
            webbrowser.open(url)
        # open solutions page from default browser
        elif key == 'S':
            url = self.get_solutions_url()
            webbrowser.open(url)
        else:
            return urwid.Frame.keypress(self, size, key)

    def edit_code(self, newcode):
        filepath = edit_code(self.quiz.id, self.quiz.sample_code, newcode)
        # open editor to edit code
        edit(filepath, self.loop)

    def get_discussion_url(self):
        return f"{BASE_URL}/problems/{self.quiz.slug}/discuss"

    def get_solutions_url(self):
        return f"{BASE_URL}/problems/{self.quiz.slug}/solution"
