import os
import re
import subprocess
import webbrowser
import urwid
from .viewhelper import vim_key_map
from ..code import *
from ..leetcode import BASE_URL

class DetailView(urwid.Frame):
    '''
        Quiz Item Detail View
    '''
    def __init__(self, data, config, loop = None):
        self.data = data
        self.config = config
        self.loop = loop
        blank = urwid.Divider()
        view_title = urwid.AttrWrap(urwid.Text(self.data.title), 'body')
        view_text = self.make_body_widgets()
        view_code_title = urwid.Text('\n --- Sample Code ---\n')
        view_code = urwid.Text(self.data.code)
        listitems = [blank, view_title, blank] + view_text + \
                    [blank, view_code_title, blank, view_code, blank]
        self.listbox = urwid.ListBox(urwid.SimpleListWalker(listitems))
        urwid.Frame.__init__(self, self.listbox)

    def make_body_widgets(self):
        newline = 0
        tags = False
        text_widgets = []
        for line in self.data.body.split('\n'):
            if line == '' and tags:
                newline = newline + 1
                if newline >= 2:
                    tags = False
            else:
                if re.search('Show Tags', line):
                    newline = 0
                    tags = True
                elif tags:
                    text_widgets.append(urwid.Text(('tag', line)))
                    continue
            text_widgets.append(urwid.Text(line))
        return text_widgets

    def keypress(self, size, key):
        key = vim_key_map(key)
        ignore_key = ('l', 'right', 'enter')
        if key in ignore_key:
            pass
        # edit sample code
        if key is 'e':
            self.edit_code()
        # open discussion page from default browser
        elif key is 'd':
            url = self.get_discussion_url()
            webbrowser.open(url)
        else:
            return urwid.Frame.keypress(self, size, key)

    def edit_code(self):
        if not self.config.path:
            return
        if not os.path.exists(self.config.path):
            os.makedirs(self.config.path)

        filepath = os.path.join(self.config.path, str(self.data.id) + '.' + self.config.ext)
        code = prepare_code(self.data.code, self.config.language, filepath)
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(code)
        cmd = os.environ.get('EDITOR', 'vi') + ' ' + filepath
        current_directory = os.getcwd()
        if is_inside_tmux():
            open_in_new_tmux_window(cmd)
        else:
            os.chdir(self.config.path)
            subprocess.call(cmd, shell=True)
            delay_refresh_detail(self.loop)
        os.chdir(current_directory)

    def get_discussion_url(self):
        item_url = self.data.url.strip('/')
        name = item_url.split('/')[-1]
        url = BASE_URL + '/discuss/questions/oj/' + name
        return url


@enhance_code
@generate_makefile
def prepare_code(code, language, filepath):
    return code


