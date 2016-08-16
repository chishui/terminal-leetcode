import os
import re
import webbrowser
import urlparse
import urwid
import subprocess
from .model import QuizItem
from .code import enhance_code, generate_makefile
from .leetcode import BASE_URL

def vim_key_map(key):
    if key == 'j':
        return 'down'
    if key == 'k':
        return 'up'
    if key == 'h':
        return 'left'
    if key == 'l':
        return 'right'
    if key == 'ctrl f':
        return 'page down'
    if key == 'ctrl b':
        return 'page up'
    return key

class ItemWidget(urwid.WidgetWrap):
    def __init__(self, data, sel=True):
        self.sel = sel
        self.id = data.id
        self.data = data
        lockbody = 'body' if not self.data.lock else 'lock'
        pass_symbol = u''
        if data.pass_status == 'ac':
            pass_symbol = u'\u2714'
        elif data.pass_status == 'notac':
            pass_symbol = u'\u2718'
        text = str(data.id).ljust(4) + pass_symbol
        self.item = [
            ('fixed', 15, urwid.Padding(urwid.AttrWrap(
                urwid.Text(text),
                lockbody, 'focus'), left=2)),
            urwid.AttrWrap(urwid.Text('%s' % data.title), lockbody, 'focus'),
            (15, urwid.AttrWrap(urwid.Text('%s' % data.acceptance), lockbody, 'focus')),
            (15, urwid.AttrWrap(urwid.Text('%s' % data.difficulty), lockbody, 'focus')),
        ]
        w = urwid.Columns(self.item)
        super(ItemWidget, self).__init__(w)

    def selectable(self):
        return self.sel and not self.data.lock

    def keypress(self, size, key):
        return vim_key_map(key)


class DetailView(urwid.Frame):
    def __init__(self, data, config):
        self.data = data
        self.config = config
        blank = urwid.Divider()
        view_title = urwid.AttrWrap(urwid.Text(self.data.title), 'body')
        view_text = self.make_body_widgets()
        view_code_title = urwid.Text('\n --- Sample Code ---\n')
        view_code = urwid.Text(self.data.code)
        listitems = [blank, view_title, blank] + view_text + \
                    [blank, view_code_title, blank, view_code, blank]
        listbox = urwid.ListBox(urwid.SimpleListWalker(listitems))
        urwid.Frame.__init__(self, listbox)

    def make_body_widgets(self):
        newline = 0
        tags = False
        text_widgets = []
        for line in self.data.body.split('\n'):
            if line == '':
                newline = newline + 1
                if newline >= 2:
                    tags = False
            else:
                newline = 0
                if re.search('Show Tags', line):
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
        if self.config.path == '':
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
        os.chdir(self.config.path)
        subprocess.call(cmd, shell=True)
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


class HelpView(urwid.Frame):
    '''
        basic:
                'UP' or 'k'                 : up
                'DOWN' or 'j'               : down
                'LEFT' or 'h'               : go to quiz list
                'RIGHT' or 'ENTER' or 'l'   : see quiz detail
                'PageUp'                    : see previous page
                'PageDown'                  : see next page
        sort:
                '1'                         : sort by id
                '2'                         : sort by title
                '3'                         : sort by acceptance
                '4'                         : sort by difficulty
        others:
                'q'                         : quit
                'H'                         : help
                'R'                         : retrieve quiz list from website
                'f'                         : search quiz by id
                'e'                         : open editor to edit code
                'd'                         : open discussion in web browser
    '''

    def __init__(self):
        title = urwid.AttrWrap(urwid.Text('Help'), 'body')
        body = urwid.Text(HelpView.__doc__)
        pile = urwid.Pile([title, body])
        filler = urwid.Filler(pile)
        urwid.Frame.__init__(self, filler)

    def keypress(self, size, key):
        ignore_key = ('H', 'l', 'right', 'enter')
        if key in ignore_key:
            pass
        else:
            return urwid.Frame.keypress(self, size, key)


class HomeView(urwid.Frame):
    def __init__(self, data, header):
        title = [
            ('fixed', 15, urwid.Padding(urwid.AttrWrap(
                urwid.Text('#'),
                'body', 'focus'), left=2)),
            urwid.AttrWrap(urwid.Text('Title'), 'body', 'focus'),
            (15, urwid.AttrWrap(urwid.Text('Acceptance'), 'body', 'focus')),
            (15, urwid.AttrWrap(urwid.Text('Difficulty'), 'body', 'focus')),
        ]
        title_column = urwid.Columns(title)
        items = make_itemwidgets(data)
        self.listbox = urwid.ListBox(urwid.SimpleListWalker(items))
        header_pile = urwid.Pile([header, title_column])
        urwid.Frame.__init__(self, urwid.AttrWrap(self.listbox, 'body'), header=header_pile)
        self.last_sort = {'attr': 'id', 'reverse': True}

    def sort_list(self, attr, cmp=None):
        if attr == self.last_sort['attr']:
            self.last_sort['reverse'] = not self.last_sort['reverse']
        else:
            self.last_sort['reverse'] = False
            self.last_sort['attr'] = attr

        self.listbox.body.sort(key=lambda x: getattr(x.data, attr),
                               reverse=self.last_sort['reverse'],
                               cmp=cmp)

    def difficulty_cmp(self, x, y):
        d = {'Easy': 0, 'Medium': 1, 'Hard': 2}
        x = d[x]
        y = d[y]
        return cmp(x, y)

    def keypress(self, size, key):
        key = vim_key_map(key)
        ignore_key = ('h', 'left')
        if key in ignore_key:
            pass
        elif key is '1':
            self.sort_list('id')
        elif key is '2':
            self.sort_list('title')
        elif key is '3':
            self.sort_list('acceptance')
        elif key is '4':
            self.sort_list('difficulty', cmp=self.difficulty_cmp)
        else:
            return urwid.Frame.keypress(self, size, key)


def make_itemwidgets(data):
    items = []
    for item in data:
        items.append(ItemWidget(item))
    return items
