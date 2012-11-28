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
