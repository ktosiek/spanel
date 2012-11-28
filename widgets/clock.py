import gtk
import gobject
from time import strftime


class ClockWidget(gtk.Label):
    def __init__(self):
        super(ClockWidget, self).__init__()
        self.update()
        gobject.timeout_add(990, self.update)

    def update(self):
        self.set_text(strftime('%Y.%m.%d %H:%M:%S'))
        self.queue_draw()
        return True
