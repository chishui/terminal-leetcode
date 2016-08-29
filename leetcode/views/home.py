import urwid
from .viewhelper import vim_key_map

class ItemWidget(urwid.WidgetWrap):
    '''
        Quiz List Item View
    '''
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
        urwid.WidgetWrap.__init__(self, w)

    def selectable(self):
        return self.sel and not self.data.lock

    def keypress(self, size, key):
        return key


class HomeView(urwid.Frame):
    '''
        Quiz List View
    '''
    def __init__(self, data, header, terminal=None):
        self.terminal = terminal
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
        elif key is 'R':
            if self.terminal:
                self.terminal.reload_list()
        elif key in ('enter', 'right'):
            if  self.listbox.get_focus()[0].selectable() and self.terminal:
                self.terminal.enter_detail(self.listbox.get_focus()[0].data)
        elif key is 'f':
            if self.terminal:
                self.terminal.enter_search()
        elif key is 'home':
            self.listbox.focus_position = 0
        elif key is 'end':
            self.listbox.focus_position = len(self.listbox.body) - 1
        else:
            return urwid.Frame.keypress(self, size, key)


def make_itemwidgets(data):
    items = []
    for item in data:
        items.append(ItemWidget(item))
    return items
