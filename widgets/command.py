# Copyright 2012 Tomasz Kontusz
#
# This file is part of Spanel.
#
# Spanel is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Spanel is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Spanel. If not, see <http://www.gnu.org/licenses/>.

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
