import urwid


class HelpView(urwid.Frame):
    '''
        basic:
                'UP' or 'k'                 : up
                'DOWN' or 'j'               : down
                'LEFT' or 'h'               : go to quiz list
                'RIGHT' or 'ENTER' or 'l'   : see quiz detail
                'PageUp'                    : see previous page
                'PageDown'                  : see next page
                'Home'                      : go to the first quiz
                'End'                       : go to the last quiz
        sort:
                '1'                         : sort by id
                '2'                         : sort by title
                '3'                         : sort by acceptance
                '4'                         : sort by difficulty
        others:
                'q'                         : quit
                'H'                         : help
                'R'                         : retrieve quiz list from website
                'f'                         : search quiz
                'n'                         : search next quiz (quiz home view)
                'e'                         : open editor to edit code
                'n'                         : create a new file to edit sample code (quiz detail view)
                'd'                         : open discussion in web browser
                's'                         : submit your code to leetcode (quiz detail view)
                'S'                         : open solutions in web browser
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
