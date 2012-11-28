#!/usr/bin/env python
import sys
import threading
import gtk
import gobject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from utils import GdkLock
from widgets.i3_ws import I3Workspaces
from widgets.clock import ClockWidget
from widgets.command import CommandWidget
from widgets.notify import NotificationsWidget

height = 16

class PanelWindow(gtk.Window):
    def __init__(self):
        super(PanelWindow, self).__init__(gtk.WINDOW_TOPLEVEL)
        self.set_default_size(gtk.gdk.screen_width(), height)
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DOCK)
        self.move(0, gtk.gdk.screen_height()-height)
        self._box = gtk.HBox()
        self.add(self._box)
        self.setup_widgets()
        self.show_all()
        self.window.property_change("_NET_WM_STRUT", "CARDINAL", 32,
            gtk.gdk.PROP_MODE_REPLACE, [0, 0, 0, height])

    def setup_widgets(self):
        self._box.pack_start(I3Workspaces(), expand=False)

        self._box.pack_start(gtk.HSeparator(), expand=True, fill=True)

        self._box.pack_start(NotificationsWidget(), expand=False)
        self._box.pack_start(
            CommandWidget('cat /proc/loadavg | cut -d" " -f 1,2,3', 5000),
            expand=False, padding=5)
        self._box.pack_start(ClockWidget(), expand=False)


def main():
    app = PanelWindow()
    gtk.gdk.threads_init()
    with GdkLock():
        gtk.main()


if __name__ == '__main__':
    main()
