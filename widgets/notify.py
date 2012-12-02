from collections import OrderedDict
import logging
import os

import gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from utils import GdkLock, Singleton


logger = logging.getLogger(__name__)


ICON_SIZE = 4
ICON_SIDE = 16


class DBusSignatureBuilder(unicode):
    """Builder for DBus signature"""
    def __init__(self, arg=''):
        super(DBusSignatureBuilder, self).__init__(arg)

    def __getattr__(self, attr):
        return type(self)(self + {
            'string': 's', 'variant': 'v',
            'uint32': 'u', 'int32': 'i'
        }[attr])

    def array(self, elem):
        if len(elem) == 1:
            return type(self)('%sa%s' % (self, elem))
        else:
            return type(self)('%sa(%s)' % (self, elem))

    def dict(self, elem):
        return type(self)('%sa{%s}' % (self, elem))


sig = DBusSignatureBuilder()


class Notification(object):
    def __init__(self, app, n_id, summary, body, actions, icon, hints, expire):
        for attr in ('app', 'n_id', 'summary', 'body', 'actions', 'icon',
                     'hints', 'expire'):
            setattr(self, attr, locals()[attr])

    def __unicode__(self):
        ret = '%s: %s' % (self.app, self.summary)
        if self.body:
            ret += ', ' + self.body[:50]
            if len(self.body) > 50:
                ret += '...'
        return ret

    def __repr__(self):
        return u'<(%i) %s: %s>' % (self.n_id, self.__class__.__name__,
                                   unicode(self))


dbus_name = 'org.freedesktop.Notifications'

class NotificationDaemon(dbus.service.Object):
    _metaclass_ = Singleton

    def __init__(self, listeners=[]):
        DBusGMainLoop(set_as_default=True)
        self.notifications = {}
        self.listeners = listeners
        bus_name = dbus.service.BusName(dbus_name, bus=dbus.SessionBus(),
                                        do_not_queue=True,
                                        replace_existing=True)
        dbus.service.Object.__init__(
            self, bus_name=bus_name,
            object_path='/org/freedesktop/Notifications')

    def listeners_each(self, fun):
        """Run fun(listener) for all listeners"""
        for l in self.listeners:
            try:
                fun(l)
            except Exception:
                logger.exception('Problem with call to listener %s', repr(l))


    @dbus.service.method(dbus_name, out_signature='ssss')
    def GetServerInformation(self):
        return ('spanel', 'tk', '0.1', '0.9')

    @dbus.service.method(dbus_name, in_signature='',
                         out_signature=sig.array(sig.string))
    def GetCapabilities(self):
        return [
            'actions', # buttons under notification
            'body', # implementation shows the body of message
            'icon-static', # only show static icons
            'persistence', # TODO: wat
        ]

    @dbus.service.method(dbus_name,
                         in_signature=sig.string.uint32.string.string.string. \
                            array(sig.string).dict(sig.string.variant).int32,
                         out_signature=sig.uint32)
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions,
               hints, expire):
        n_id = replaces_id or max([0] + self.notifications.keys()) + 1
        self.notifications[n_id] = Notification(app_name, n_id, summary, body,
                                                actions, app_icon, hints,
                                                expire)
        self.listeners_each(lambda l: l.notify(self, n_id))
        return n_id

    @dbus.service.method(dbus_name, in_signature='u', out_signature='')
    def CloseNotification(self, n_id):
        if n_id in self.notifications:
            self.NotificationClosed(n_id, 3)

    @dbus.service.signal(dbus_name, signature=sig.uint32.uint32)
    def NotificationClosed(self, n_id, reason):
        """reasons:
            1 - The notification expired.
            2 - The notification was dismissed by the user.
            3 - The notification was closed by a call to CloseNotification.
            4 - Undefined/reserved reasons.
            """
        logger.debug('Closing notification %s, reason %s',
            self.notifications[n_id], reason)
        self.listeners_each(lambda l: l.close(self, n_id))
        del self.notifications[n_id]

    @dbus.service.signal(dbus_name, signature=sig.uint32.string)
    def ActionInvoked(self, n_id, action_key):
        pass


class NotificationObserver(object):
    def notify(self, daemon, notification_id):
        pass

    def close(self, daemon, notification_id):
        pass


class NotificationsWidget(gtk.HBox, NotificationObserver):
    def __init__(self):
        super(NotificationsWidget, self).__init__()
        self.daemon = NotificationDaemon(listeners=[self])
        self.notifications = OrderedDict()
        self._gdk_lock = GdkLock()

    def _get_notification_by_id(self, n_id):
        for _, notifs in self.notifications.items():
            for n in notifs:
                if n.n_id == n_id:
                    return n

    def notify(self, daemon, n_id):
        notif = daemon.notifications[n_id]
        logger.debug('Received notification %s', notif)
        old_notif = self._get_notification_by_id(n_id)
        if old_notif:
            self.update_notification(old_notif, notif)
        else:
            self.add_notification(notif)
        with self._gdk_lock:
            self.refresh()

    def close(self, daemon, n_id):
        notif = self._get_notification_by_id(n_id)
        logger.debug('Removing notification %s', notif)
        self.remove_notification(notif)
        with self._gdk_lock:
            self.refresh()

    def add_notification(self, notif):
        notif_l = self.notifications.get(notif.app, [])
        notif_l.append(notif)
        if notif.app in self.notifications:
            del self.notifications[notif.app]
        self.notifications[notif.app] = notif_l

    def remove_notification(self, notif):
        self.notifications[notif.app].remove(notif)
        if len(self.notifications[notif.app]) < 1:
            del self.notifications[notif.app]

    def update_notification(self, old_notif, notif):
        self.remove_notification(old_notif)
        self.add_notification(notif)

    def refresh(self):
        for c in self.get_children():
            self.remove(c)

        if not self.notifications:
            return

        last_app = self.notifications.keys()[-1]
        for app, notifs in self.notifications.items():
            icon = AppNotificationsIcon(notifs, expanded=(app==last_app))
            eventbox = gtk.EventBox()
            eventbox.add(icon)
            eventbox.connect('button-press-event', self.notification_clicked,
                             notifs[-1].n_id)
            self.pack_end(eventbox, padding=5)
        self.show_all()
        self.queue_draw()

    def notification_clicked(self, widget, event, n_id):
        with self._gdk_lock.fake():
            self.daemon.NotificationClosed(n_id, 2)
        return True


class AppNotificationsIcon(gtk.HBox):
    """Widget for notification icon"""
    def __init__(self, notifications, expanded=False):
        super(AppNotificationsIcon, self).__init__()
        self.notifications = notifications
        notif_count = len(notifications)
        main_notif = notifications[-1]
        self.pack_start(self.prepare_notification_icon(main_notif))
        if notif_count > 1:
            self.pack_start(gtk.Label('({})'.format(notif_count)))
        if expanded:
            label = main_notif.summary
            if main_notif.body:
                label += ': {}'.format(main_notif.body)
            self.pack_start(gtk.Label(label))

    def prepare_notification_icon(self, notification):
        if 'image-data' in notification.hints:
            logger.warning("TODO: notification %s used image-data, ignoring",
                           notification)

        if notification.icon:
            if os.path.exists(notification.icon):
                icon = gtk.Image()
                pb = gtk.gdk.pixbuf_new_from_file_at_size(notification.icon,
                                                          ICON_SIDE, ICON_SIDE)
                icon.set_from_pixbuf(pb)
                return icon
            else:
                icon = gtk.Image()
                try_icons = (notification.icon,
                    notification.app,
                    notification.app.lower(),
                )
                icon_theme = gtk.icon_theme_get_default()
                for icon_name in try_icons:
                    if icon_theme.lookup_icon(icon_name, ICON_SIZE, 0):
                        icon.set_from_icon_name(icon_name, ICON_SIZE)
                        return icon
        return gtk.Label(notification.app[:10])
