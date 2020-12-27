import os
import re
import json
import urwid
from .viewhelper import vim_key_map
from ..helper.config import TAG_FILE


class ItemWidget(urwid.WidgetWrap):
    '''
        Quiz List Item View
    '''
    def __init__(self, data, marks, sel=True):
        self.sel = sel
        self.id = data.id
        self.data = data
        lockbody = 'body' if not self.data.locked else 'lock'
        pass_symbol = u''
        if self.data.submission_status == 'ac':
            pass_symbol = u'\u2714'
        elif self.data.submission_status == 'notac':
            pass_symbol = u'\u2718'
        text = str(self.data.id)
        mark = make_mark(marks, self.data.id)
        self.item = [
            (4, urwid.AttrWrap(urwid.Text(text), lockbody, 'focus')),
            (2, urwid.AttrWrap(urwid.Text(pass_symbol), lockbody, 'focus')),
            (10, urwid.AttrWrap(urwid.Text(mark), 'hometag', 'focus')),
            urwid.AttrWrap(urwid.Text('%s ' % data.title + (u'\u2605'if self.data.favorite else '')), lockbody, 'focus'),
            (15, urwid.AttrWrap(urwid.Text('%s' % data.acceptance), lockbody, 'focus')),
            (15, urwid.AttrWrap(urwid.Text('%s' % data.difficulty), lockbody, 'focus')),
        ]
        w = urwid.Columns(self.item)
        urwid.WidgetWrap.__init__(self, w)

    def selectable(self):
        return self.sel and not self.data.locked

    def keypress(self, size, key):
        return key


class HomeView(urwid.Frame):
    '''
        Quiz List View
    '''
    def __init__(self, data, header):
        title = [
            (4, urwid.AttrWrap(urwid.Text('#'), 'body', 'focus')),
            (2, urwid.AttrWrap(urwid.Text(''), 'body', 'focus')),
            (10, urwid.AttrWrap(urwid.Text('Tag'), 'body', 'focus')),
            urwid.AttrWrap(urwid.Text('Title'), 'body', 'focus'),
            (15, urwid.AttrWrap(urwid.Text('Acceptance'), 'body', 'focus')),
            (15, urwid.AttrWrap(urwid.Text('Difficulty'), 'body', 'focus')),
        ]
        title_column = urwid.Columns(title)
        self.marks = load_marks()
        items = make_itemwidgets(data, self.marks)
        self.listbox = urwid.ListBox(urwid.SimpleListWalker(items))
        header_pile = urwid.Pile([header, title_column])
        urwid.Frame.__init__(self, urwid.AttrWrap(self.listbox, 'body'), header=header_pile)
        self.last_sort = {'attr': 'id', 'reverse': True}
        self.last_search_text = None

    def sort_list(self, attr, conversion=None):
        if attr == self.last_sort['attr']:
            self.last_sort['reverse'] = not self.last_sort['reverse']
        else:
            self.last_sort['reverse'] = False
            self.last_sort['attr'] = attr

        if conversion:
            self.listbox.body.sort(key=lambda x: conversion(getattr(x.data, attr)),
                                   reverse=self.last_sort['reverse'])
        else:
            self.listbox.body.sort(key=lambda x: getattr(x.data, attr),
                                   reverse=self.last_sort['reverse'])

    def difficulty_conversion(self, x):
        d = {'Easy': 0, 'Medium': 1, 'Hard': 2}
        return d[x]

    def keypress(self, size, key):
        key = vim_key_map(key)
        ignore_key = ('h', 'left')
        if key in ignore_key:
            pass
        elif key == '1':
            self.sort_list('id')
        elif key == '2':
            self.sort_list('title')
        elif key == '3':
            self.sort_list('acceptance')
        elif key == '4':
            self.sort_list('difficulty', conversion=self.difficulty_conversion)
        elif key == 'home':
            self.listbox.focus_position = 0
        elif key == 'end':
            self.listbox.focus_position = len(self.listbox.body) - 1
        elif key == 'n':
            self.handle_search(self.last_search_text, True)
        else:
            return urwid.Frame.keypress(self, size, key)

    def handle_search(self, text, from_current=False):
        self.last_search_text = text
        if text == '':
            return
        cur = self.listbox.focus_position if from_current else 0
        if is_string_an_integer(text):
            for i in range(len(self.listbox.body)):
                item = self.listbox.body[i]
                if item.data.id == int(text):
                    self.listbox.focus_position = i
                    break
        else:
            for i in range(cur + 1, len(self.listbox.body)):
                item = self.listbox.body[i]
                if re.search('.*(%s).*' % text, item.data.title, re.I):
                    self.listbox.focus_position = i
                    break

    def is_current_item_enterable(self):
        return self.listbox.get_focus()[0].selectable()

    def get_current_item_data(self):
        return self.listbox.get_focus()[0].data


def make_itemwidgets(data, marks):
    items = []
    for quiz in data:
        items.append(ItemWidget(quiz, marks=marks))
    return items


def is_string_an_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def load_marks():
    if not os.path.exists(TAG_FILE):
        return {}
    with open(TAG_FILE, 'r') as f:
        return json.load(f)


def make_mark(marks, quiz_id):
    quiz_id = str(quiz_id)
    if quiz_id not in marks:
        return ''
    return ' '.join(marks[quiz_id])
