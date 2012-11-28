import gtk
import gobject

import subprocess


class CommandWidget(gtk.Label):
    def __init__(self, cmd, interval):
        self.cmd = cmd
        super(CommandWidget, self).__init__()
        gobject.timeout_add(interval, self.update)
        self.update()

    def update(self):
        p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        self.set_text('|'.join(out.splitlines()))
        self.queue_draw()
        return True
