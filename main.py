#!/usr/bin/env python
import argparse
import logging
import sys
import threading

import gtk
import gobject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from utils import Enum, GdkLock

# setting DEBUG for pre-main initialization, it will be changed in main()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    logger.info('loading configuration')
    import conf

    debug_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

    parser = argparse.ArgumentParser(
        description="Simple panel written in Python for holding widgets")
    parser.add_argument('--verbosity', '-v', dest='verbosity',
                        choices=debug_levels, default=None)

    args = parser.parse_args()

    level = args.verbosity or getattr(conf, 'VERBOSITY', 'INFO')
    if level not in debug_levels:
        logger.critical('Log level %s not supported!', level)
        return 1
    logging.basicConfig(level=level)

    logger.info('creating panel')
    app = PanelWindow(position=getattr(conf, 'POSITION', None),
                      widgets=getattr(conf, 'WIDGETS', []))
    logger.info('starting main loop')
    gtk.gdk.threads_init()
    with GdkLock():
        gtk.main()


if __name__ == '__main__':
    main()
