import asyncio
import threading
import time
from pydbus import SystemBus
from gi.repository import GLib
import websocket

SERVER_URI = "ws://192.168.x.xx:9080"

# BLE Setting
ADAPTER_IFACE = 'org.bluez.Adapter1'
LE_ADV_MGR_IFACE = 'org.bluez.LEAdvertisingManager1'
ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
BUS = SystemBus()

current_advertisement = None


class Advertisement:
    def __init__(self, bus, index, ad_type, local_name):
        self.path = "/org/bluez/example/advertisement{}".format(index)
        self.bus = bus
        self.ad_type = ad_type
        self.local_name = local_name

    def get_properties(self):
        return {
            ADVERTISEMENT_IFACE: {
                'Type': self.ad_type,
                'LocalName': self.local_name,
                'ServiceUUIDs': ['12345678-1234-5678-1234-56789abcdef0'],
                'IncludeTxPower': True
            }
        }

    def get_path(self):
        return self.path

    def Release(self):
        print("Advertisement {} released".format(self.local_name))


def find_adapter_path():
    mngr = BUS.get("org.bluez", "/")
    objects = mngr.GetManagedObjects()
    for path, ifaces in objects.items():
        if ADAPTER_IFACE in ifaces:
            return path
    raise RuntimeError("No BLE adapter found")


adapter_path = find_adapter_path()
adapter = BUS.get("org.bluez", adapter_path)
adapter.Powered = True


def advertise_event(event_name: str):
    global current_advertisement
    if current_advertisement:
        try:
            adv_mgr = BUS.get("org.bluez", adapter_path)
            adv_mgr.UnregisterAdvertisement(current_advertisement.get_path())
            print("Unregistered previous ad: {}".format(
                current_advertisement.local_name))
        except Exception as e:
            print("Unregister error:", e)

    current_advertisement = Advertisement(BUS, 0, "peripheral", event_name)

    BUS.register_object(
        current_advertisement.get_path(),
        {
            ADVERTISEMENT_IFACE: {
                'Release': current_advertisement.Release
            }
        },
        current_advertisement.get_properties()
    )

    adv_mgr = BUS.get("org.bluez", adapter_path)
    adv_mgr.RegisterAdvertisement(
        current_advertisement.get_path(), {},
        reply_handler=handle_advertise_reply,
        error_handler=handle_advertise_error
    )


def handle_advertise_reply():
    print("Now advertising")


def handle_advertise_error(e):
    print("Failed to advertise:", str(e))


def on_message(ws, message):
    try:
        if isinstance(message, bytes):
            message = message.decode('utf-8')

        if isinstance(message, dict):
            print("Unexpected dict received via WebSocket:", message)
            return

        message = message.strip()
        print("Received from Godot:", message)
        advertise_event(message)

    except Exception as e:
        print("WebSocket error:", e)


def on_error(ws, error):
    print("WebSocket error:", error)


def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")


def on_open(ws):
    print("WebSocket connected to server")


def run_websocket():
    ws = websocket.WebSocketApp(
        SERVER_URI,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()


if __name__ == "__main__":
    ble_loop = threading.Thread(target=GLib.MainLoop().run, daemon=True)
    ble_loop.start()

    run_websocket()
