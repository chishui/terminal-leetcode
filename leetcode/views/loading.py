import time
from threading import Thread
import urwid
from .viewhelper import delay_refresh
from ..helper.model import EasyLock


class LoadingView(urwid.Frame):
    '''
        Loading View When Doing HTTP Request
    '''
    def __init__(self, text, width, host_view, loop=None):
        self.running = False
        self.lock = EasyLock()
        self.loop = loop
        self.overlay = urwid.Overlay(
            urwid.LineBox(urwid.Text(text)), host_view,  # urwid.SolidFill(),
            'center', width, 'middle', None)
        urwid.Frame.__init__(self, self.overlay)

    def keypress(self, size, key):
        pass

    def set_text(self, text):
        with self.lock:
            self.overlay.contents[1][0].base_widget.set_text(text)

    @property
    def is_running(self):
        return self.t and self.t.is_alive()

    def start(self):
        self.running = True
        self.t = Thread(target=self.work)
        self.t.start()

    def end(self):
        self.running = False
        self.t.join()

    def work(self):
        while self.running:
            with self.lock:
                text = self.overlay.contents[1][0].base_widget.text
                num = text.count('.')
                if num < 3:
                    text = text + '.'
                else:
                    text = text.strip('.')
                self.overlay.contents[1][0].base_widget.set_text(text)
            delay_refresh(self.loop)
            time.sleep(0.8)


class Toast(urwid.Frame):
    '''
        Toast View
    '''
    def __init__(self, text, width, host_view, loop=None):
        self.loop = loop
        self.host_view = host_view
        self.overlay = urwid.Overlay(
            urwid.LineBox(urwid.Text(text)), host_view,  # urwid.SolidFill(),
            'center', width, 'middle', None)
        urwid.Frame.__init__(self, self.overlay)

    def keypress(self, size, key):
        self.destroy()

    def show(self):
        self.loop.widget = self

    def destroy(self):
        self.loop.widget = self.host_view
