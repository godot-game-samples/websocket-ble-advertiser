import threading
from gi.repository import GLib

from ble_broadcaster import BLEBroadcaster
from ws_client import BLEWebSocketClient

if __name__ == "__main__":
    ble = BLEBroadcaster()

    # Running GLib.MainLoop in the background
    threading.Thread(target=GLib.MainLoop().run, daemon=True).start()

    # Start WebSocket client
    ws = BLEWebSocketClient("ws://192.168.3.xx:9080", ble.advertise)
    ws.start()
