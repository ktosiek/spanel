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
