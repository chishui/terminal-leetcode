import os
import re
import subprocess
import webbrowser
import urwid
import logging
from .viewhelper import vim_key_map
from ..code import *
from ..leetcode import BASE_URL
from ..editor import edit
from ..config import config

class DetailView(urwid.Frame):
    '''
        Quiz Item Detail View
    '''
    def __init__(self, quiz, loop = None):
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
        newline = 0
        tags = False
        text_widgets = []

        for line in self.quiz.content.split('\n'):
            text_widgets.append(urwid.Text(line))

        text_widgets.append(urwid.Divider())

        for tag in self.quiz.tags:
            text_widgets.append(urwid.Text(('tag', tag)))

        return text_widgets

    def keypress(self, size, key):
        key = vim_key_map(key)
        ignore_key = ('l', 'right', 'enter')
        if key in ignore_key:
            pass
        # edit sample code
        if key is 'e':
            self.edit_code()
        # edit new sample code
        elif key is 'n':
            self.edit_code(True)
        # open discussion page from default browser
        elif key is 'd':
            url = self.get_discussion_url()
            webbrowser.open(url)
        # open solutions page from default browser
        elif key is 'S':
            url = self.get_solutions_url()
            webbrowser.open(url)
        else:
            return urwid.Frame.keypress(self, size, key)

    def edit_code(self, newcode=False):
        filepath = get_code_file_path(self.quiz.id)
        if newcode:
            filepath = unique_file_name(filepath)

        code = prepare_code(self.quiz.sample_code, config.language, filepath)
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                #if config.keep_quiz_detail:
                    #write_quiz_detail(self.data, f)
                f.write(code)
        # open editor to edit code
        edit(filepath, self.loop)

    def get_discussion_url(self):
        item_url = self.quiz.url.strip('/')
        name = item_url.split('/')[-1]
        url = self.quiz.discussion_url + '/' + name
        return url

    def get_solutions_url(self):
        item_url = self.quiz.url.strip('/')
        name = item_url.split('/')[-1]
        url = '%s/problems/%s/#/solutions' % (BASE_URL, name)
        return url



@enhance_code
@generate_makefile
def prepare_code(code, language, filepath):
    return code
