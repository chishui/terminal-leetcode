import urwid
from .model import QuizItem

def vim_key_map(key):
    if key == 'j':
        return 'down'
    if key == 'k':
        return 'up'
    if key == 'h':
        return 'left'
    if key == 'l':
        return 'right'
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
        self.item = [
            ('fixed', 15, urwid.Padding(urwid.AttrWrap(
                urwid.Text(' %s %s' % (str(data.id), pass_symbol)),
                lockbody, 'focus'), left=2)),
            urwid.AttrWrap(urwid.Text('%s' % data.title), lockbody, 'focus'),
            (15, urwid.AttrWrap(urwid.Text('%s' % data.acceptance), lockbody, 'focus')),
            (15, urwid.AttrWrap(urwid.Text('%s' % data.difficulty), lockbody, 'focus')),
        ]
        #text = str(id).ljust(15) + title[:80].ljust(80) +
        #acceptance.ljust(15) + difficulty.ljust(15)
        #self.item = [
            #urwid.AttrWrap(urwid.Text(text), 'body', 'focus')
        #]
        w = urwid.Columns(self.item)
        super(ItemWidget, self).__init__(w)

    def selectable(self):
        return self.sel and not self.data.lock

    def keypress(self, size, key):
        return vim_key_map(key)


class DetailView(urwid.Frame):
    def __init__(self, title, body, code):
        self.title = title
        self.body = body
        self.code = code
        blank = urwid.Divider()
        view_title = urwid.AttrWrap(urwid.Text(self.title), 'body')
        view_text = urwid.Text(self.body)
        view_code_title = urwid.Text('\n --- Sample Code ---\n')
        view_code = urwid.Text(self.code)
        listitems = [
            blank,
            view_title,
            blank,
            view_text,
            blank,
            view_code_title,
            blank,
            view_code,
            blank,
        ]
        listbox = urwid.ListBox(urwid.SimpleListWalker(listitems))
        urwid.Frame.__init__(self, listbox)

    def keypress(self, size, key):
        key = vim_key_map(key)
        ignore_key = ('l', 'right', 'enter')
        if key in ignore_key:
            pass
        else:
            return urwid.Frame.keypress(self, size, key)


class HelpView(urwid.Frame):
    def __init__(self):
        title = urwid.AttrWrap(urwid.Text('Help'), 'body')
        body = urwid.Text('''
                'UP' or 'k'                 : up
                'DOWN' or 'j'               : down
                'LEFT' or 'h'               : go to quiz list
                'RIGHT' or 'ENTER' or 'l'   : see quiz detail
                'PageUp'                    : see previous page
                'PageDown'                  : see next page

                'q'                         : quit
                'H'                         : help
                'R'                         : retrieve quiz list from website
        ''')
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
        items = make_itemwidgets(data)
        self.listbox = urwid.ListBox(urwid.SimpleListWalker(items))
        urwid.Frame.__init__(self, urwid.AttrWrap(self.listbox, 'body'), header=header)

    def keypress(self, size, key):
        ignore_key = ('h', 'left')
        if key in ignore_key:
            pass
        else:
            return urwid.Frame.keypress(self, size, key)


def make_itemwidgets(data):
    items = []
    header = {}
    header['pass'] = 'None'
    header['id'] = '#'
    header['title'] = 'Title'
    header['url'] = 'Url'
    header['acceptance'] = 'Acceptance'
    header['difficulty'] = 'Difficulty'
    header['lock'] = False
    title = QuizItem(header)
    items.append(ItemWidget(title, False))
    for item in data:
        items.append(ItemWidget(item))
    return items
