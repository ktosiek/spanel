#!/usr/bin/env python
import sys
import threading
import gtk
import gobject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from utils import Enum, GdkLock

height = 16

Positions = Enum(('TOP', 'BOTTOM'))

class PanelWindow(gtk.Window):

    def __init__(self, position=Positions.TOP, widgets=[]):
        super(PanelWindow, self).__init__(gtk.WINDOW_TOPLEVEL)
        self.set_default_size(gtk.gdk.screen_width(), height)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DOCK)
        self._box = gtk.HBox()
        self.add(self._box)
        self.setup_widgets(widgets)
        self.show_all()
        if position == Positions.TOP:
            self.move(0, 0)
            self.window.property_change("_NET_WM_STRUT", "CARDINAL", 32,
                gtk.gdk.PROP_MODE_REPLACE, [0, height, 0, 0])
        elif position == Positions.BOTTOM:
            self.move(0, gtk.gdk.screen_height()-height)
            self.window.property_change("_NET_WM_STRUT", "CARDINAL", 32,
                gtk.gdk.PROP_MODE_REPLACE, [0, 0, 0, height])

    def setup_widgets(self, widgets):
        default_kwargs = {
            'expand': False
        }

        for widget, w_kwargs in widgets:
            kwargs = default_kwargs.copy()
            kwargs.update(w_kwargs)

            self._box.pack_start(widget, **kwargs)


def main():
    import conf
    app = PanelWindow(position=getattr(conf, 'POSITION', None),
                      widgets=getattr(conf, 'WIDGETS', []))
    gtk.gdk.threads_init()
    with GdkLock():
        gtk.main()


if __name__ == '__main__':
    main()
