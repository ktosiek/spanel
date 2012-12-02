import gtk

from main import Positions

from widgets.i3_ws import I3Workspaces
from widgets.clock import ClockWidget
from widgets.command import CommandWidget
from widgets.notify import NotificationsWidget
from widgets.tray import TrayWidget

WIDGETS = (
    (I3Workspaces(), {}),
    (gtk.HSeparator(), {'expand': True, 'fill': True}),
    (NotificationsWidget(), {}),
    (CommandWidget('acpi -b|sed "s/.*: //"', 5000), {'padding': 5}),
    (CommandWidget('cat /proc/loadavg | cut -d" " -f 1,2,3', 5000),
     {'padding': 5}),
    (ClockWidget(), {}),
    (TrayWidget(), {}),
)

POSITION = Positions.TOP
