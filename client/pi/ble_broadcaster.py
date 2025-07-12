from pydbus import SystemBus
from gi.repository import GLib
import uuid

ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'
ADAPTER_IFACE = 'org.bluez.Adapter1'


class Advertisement:
    def __init__(self, path, local_name):
        self.__dbus_xml__ = f"""
        <node>
          <interface name="{ADVERTISEMENT_IFACE}">
            <method name="Release"/>
            <property name="Type" type="s" access="read"/>
            <property name="LocalName" type="s" access="read"/>
            <property name="ServiceUUIDs" type="as" access="read"/>
            <property name="IncludeTxPower" type="b" access="read"/>
          </interface>
        </node>
        """
        self._path = path
        self.Type = "peripheral"
        self.LocalName = local_name
        self.ServiceUUIDs = ["12345678-1234-5678-1234-56789abcdef0"]
        self.IncludeTxPower = True

    def get_path(self):
        return self._path

    def Release(self):
        print(f"[BLE] Release called for {self.LocalName}")


class BLEBroadcaster:
    def __init__(self):
        self.bus = SystemBus()
        self.adapter_path = self._find_adapter_path()
        self.adapter = self.bus.get("org.bluez", self.adapter_path)
        self.adapter.Powered = True

        self.current_ad = None
        self.ad_registered = False

    def _find_adapter_path(self):
        manager = self.bus.get("org.bluez", "/")
        for path, ifaces in manager.GetManagedObjects().items():
            if ADAPTER_IFACE in ifaces:
                return path
        raise RuntimeError("No BLE adapter found")

    def advertise(self, message: str):
        print(f"[BLE] Advertising: {message}")
        assert isinstance(message, str), "Must be string"

        if self.current_ad and self.ad_registered:
            try:
                adv_mgr = self.bus.get("org.bluez", self.adapter_path)
                adv_mgr.UnregisterAdvertisement(self.current_ad.get_path())
                print(f"[BLE] Unregistered: {self.current_ad.LocalName}")
            except Exception as e:
                print("[BLE] Unregister error:", e)

        path = f"/org/bluez/example/advertisement_{uuid.uuid4().hex[:6]}"
        self.current_ad = Advertisement(path, message)

        self.bus.register_object(
            self.current_ad.get_path(),
            self.current_ad,
            self.current_ad.__dbus_xml__,
        )

        adv_mgr = self.bus.get("org.bluez", self.adapter_path)

        try:
            adv_mgr.RegisterAdvertisement(self.current_ad.get_path(), {})
            self.ad_registered = True
            print(f"[BLE] Now advertising: {message}")
        except Exception as e:
            self.ad_registered = False
            print("[BLE] Advertise failed:", e)
