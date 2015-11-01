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

import i3
import sys
import gtk

from utils import GdkLock


class Subscription(i3.Subscription):
    """daemonize it"""

    def start(self):
        self.daemon = True
        super(Subscription, self).start()


class I3Workspaces(gtk.Label):
    def __init__(self):
        super(I3Workspaces, self).__init__()
        self.workspaces = []

        Subscription(self.workspace_callback, 'workspace')

    def update(self):
        def workspace_text(w):
            t = str(w['name'])
            if w['urgent']:
                t = '>>%s<<' % t

            if w['focused']:
                t = '{%s}' % t
            elif w['visible']:
                t = '<%s>' % t

            return t

        text = ' '.join(map(workspace_text, self.workspaces))
        self.set_text(text)
        self.queue_draw()

    def workspace_callback(self, event, data, subscription):
        sys.stdout.flush()
        with GdkLock():
            self.workspaces = data
            self.update()
