import urwid
import random
from .model import QuizItem
from .leetcode import Leetcode

class ItemWidget (urwid.WidgetWrap):
    def __init__ (self, data,  sel = True):
        self.sel = sel
        self.id = data.id
        self.data = data
        lockbody = 'body' if not self.data.lock else 'lock'
        self.item = [
            ('fixed', 15, urwid.Padding(urwid.AttrWrap(
                urwid.Text(' %s' % str(data.id)), lockbody, 'focus'), left=2)),
            urwid.AttrWrap(urwid.Text('%s' % data.title), lockbody, 'focus'),
            (15, urwid.AttrWrap(urwid.Text('%s' % data.acceptance), lockbody, 'focus')),
            (15, urwid.AttrWrap(urwid.Text('%s' % data.difficulty), lockbody, 'focus')),
        ]
        #text = str(id).ljust(15) + title[:80].ljust(80) + acceptance.ljust(15) + difficulty.ljust(15)
        #self.item = [
            #urwid.AttrWrap(urwid.Text(text), 'body', 'focus')
        #]
        w = urwid.Columns(self.item)
        self.__super.__init__(w)

    def selectable (self):
        return self.sel and not self.data.lock

    def keypress(self, size, key):
        if key == 'j':
            return 'down'
        if key == 'k' :
            return 'up'
        if key == 'h':
            return 'left'
        if key == 'l':
            return 'right'
        return key

class DetailView(object):
    def __init__(self,title,body):
        self.title = title
        self.body= body

    def build(self):
        title = urwid.AttrWrap(urwid.Text(self.title), 'body')
        body = urwid.Text(self.body)
        body = urwid.Pile([title,body])
        fill = urwid.Filler(body)
        return fill

palette = [
    ('body', 'dark cyan',''),
    ('focus', 'dark red', ''),
    ('head', 'light gray', ''),
    ('lock', 'dark gray', '')
    ]

class Terminal(object) :
    def __init__(self) :
        self.home_view = None
        self.listbox = None
        self.loop = None
        self.leetcode = Leetcode()
        self.help_view = None
        self.quit_confirm_view = None
        self.view_stack = []

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

    def keystroke (self, input):
        if self.quit_confirm_view and self.current_view == self.quit_confirm_view:
            if input is 'y':
                raise urwid.ExitMainLoop()
            else:
                self.go_back()
                return

        if input in ('q', 'Q'):
            self.goto_view(self.make_quit_confirmation())

        if input is 'R':
            items = self.leetcode.hard_retrieve_home()
            self.home_view = self.make_listview(items)
            self.goto_view(self.home_view)

        if self.is_home and (input is 'l' or input is 'enter' or input is 'right'):
            title, body = self.leetcode.retrieve_detail(self.listbox.get_focus()[0].data)
            self.goto_view( self.make_detailview(title, body))

        if not self.is_home and (input is 'left' or input is 'h'):
            self.go_back()

        if input is 'H':
            self.goto_view(self.make_helpview())

    def make_quit_confirmation(self) :
        text = urwid.AttrMap(urwid.Text('Do you really want to quit ? (y/n)'), 'body')
        self.quit_confirm_view = urwid.Overlay(text, self.current_view, 'left',  ('relative', 100), 'bottom', None)
        return self.quit_confirm_view

    def make_detailview(self, title, body):
        return DetailView(title=title, body=body).build()

    def make_listview(self, data) :
        items = self.make_itemwidgets(data)
        header = urwid.AttrMap(urwid.Text('Command: q:quit, 1:sort by id, 2: sort by title 3: sort by acceptance 4: sort by difficulty'), 'head')
        self.listbox = urwid.ListBox(urwid.SimpleListWalker(items))
        self.home_view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'), header=header)
        return self.home_view

    def make_helpview(self) :
        if self.help_view:
            return self.help_view
        title = urwid.AttrWrap(urwid.Text('Help'), 'body')
        body = urwid.Text('''
                j: down
                k: up
                l/enter: see quiz detail
                h: go to quiz list
                q: quit
                H: help
                R: retrieve quiz list from website
        ''')
        body = urwid.Pile([title,body])
        self.help_view = urwid.Filler(body)
        return self.help_view

    def make_itemwidgets(self, data) :
        items = []
        title = QuizItem('#', 'Title', 'Url', 'Acceptance', 'Difficulty')
        items.append(ItemWidget(title, False))
        for item in data:
            items.append(ItemWidget(item))
        return items

    def run(self) :
        data = self.leetcode.retrieve_home()
        self.home_view = self.make_listview(data)
        self.loop = urwid.MainLoop(self.home_view, palette, unhandled_input=self.keystroke)
        self.view_stack.append(self.home_view)
        self.loop.run()


if __name__ == '__main__':
    term = Terminal()
    term.run()

