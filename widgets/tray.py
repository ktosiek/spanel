from itertools import takewhile
import logging

import gtk

from utils import Enum, Singleton


logger = logging.getLogger(__name__)


class TrayWidget(gtk.EventBox):

    _metaclass_ = Singleton

    OpCode = Enum((
        'REQUEST_DOCK',
        'BEGIN_MESSAGE',
        'CANCEL_MESSAGE',
    ))

    def __init__(self):
        super(TrayWidget, self).__init__()
        self._box = gtk.HBox()
        self.add(self._box)
        self.connect("client-event", self.client_event)

    def on_visible(self):
        if not gtk.selection_owner_set_for_display(
            gtk.gdk.display_get_default(),
            self,
            "_NET_SYSTEM_TRAY_S0", # TODO: this should be the actual screen
            gtk.gdk.CURRENT_TIME):
            raise Exception("Cannot get _NET_SYSTEM_TRAY_S0")

    def client_event(self, widget, event):
        logger.debug("received client event of type %s from %s",
                     event.message_type, event.window)
        if event.message_type == "_NET_SYSTEM_TRAY_OPCODE":
            data = TrayWidget.parse_xevent_data(event.data, event.data_format)
            timestamp = data[0]
            opcode = data[1]
            logger.debug("...with opcode %i (%s)", opcode,
                         self.OpCode[opcode])
            if opcode == self.OpCode.REQUEST_DOCK:
                icon_wid = data[2]
                self.add_icon(timestamp, icon_wid)
            elif opcode == self.OpCode.BEGIN_MESSAGE:
                timeout, msg_len, msg_id = data[2:5]
                self.receive_message(event.window, msg_len, msg_id, timeout)
            elif opcode == self.OpCode.CANCEL_MESSAGE:
                msg_id = data[2]
                self.cancel_message(event.window, msg_id)
            return True  # This event was handled here, so stop propagation
        elif event.message_type == "_NET_SYSTEM_TRAY_MESSAGE_DATA":
            data = TrayWidget.parse_xevent_data(event.data, event.data_format)
            raw_data = ''.join(imap(chr, takewhile(lambda x: x, data)))
            self.continue_message(event.window, raw_data)
            return True

    def add_icon(self, timestamp, icon_window_id):
        logger.debug("Icon 0x%x", icon_window_id)
        socket = gtk.Socket()
        self._box.add(socket)
        socket.show()
        socket.add_id(icon_window_id)
        self.queue_draw()

    def receive_message(self, window, msg_len, msg_id, timeout):
        # TODO
        logger.debug("Msg %i from %s", msg_id, window)

    def continue_message(self, window, data):
        # TODO
        logger.debug("Msg data from %s: '%s'", window, data)

    def cancel_message(self, window, msg_id):
        # TODO
        logger.debug("Cancel msg %i from %s", msg_id, window)

    @staticmethod
    def parse_xevent_data(raw_data, data_format):
        # values may be 64 bit for 32 bit format somehow,
        # so I'm baseing length of value on length of data.
        # Data should be 20 elements long.
        v_len = (len(raw_data)/20) * (data_format/8)
        data = [0] * (len(raw_data)/v_len)
        # reversed because of endianness
        for i, c in reversed(list(enumerate(raw_data))):
            data[i/v_len] <<= v_len
            data[i/v_len] |= ord(c)
        return data
