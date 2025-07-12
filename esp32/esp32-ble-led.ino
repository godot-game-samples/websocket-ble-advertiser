#include <BLEDevice.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

#define LED_PIN 2

bool ledState = false;

BLEScan* pBLEScan;
unsigned long lastScanTime = 0;
const unsigned long scanInterval = 200;

void logIfTargetDevice(BLEAdvertisedDevice& device, const String& name) {
  if (name == "LED_ON" || name == "LED_OFF") {
    Serial.println("==== BLE Device Found ====");
    Serial.print("Name: ");
    Serial.println(name.c_str());
    Serial.print("Address: ");
    Serial.println(device.getAddress().toString().c_str());
    Serial.print("RSSI: ");
    Serial.println(device.getRSSI());
    Serial.print("Advertised Service UUIDs: ");
    Serial.println(device.getServiceUUID().toString().c_str());
  }
}

void handleLedCommand(const String& name) {
  if (name == "LED_ON" && !ledState) {
    digitalWrite(LED_PIN, HIGH);
    ledState = true;
    Serial.println("[LED] Turned ON");
  } else if (name == "LED_OFF" && ledState) {
    digitalWrite(LED_PIN, LOW);
    ledState = false;
    Serial.println("[LED] Turned OFF");
  }
}

class MyAdvertisedDeviceCallbacks : public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice advertisedDevice) override {
    String name = advertisedDevice.getName();
    if (name.isEmpty()) return;

    Serial.print("🔎 Detected device name: ");
    Serial.println(name.c_str());

    // logIfTargetDevice(advertisedDevice, name);
    handleLedCommand(name);
  }
};

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("[ESP32] Starting BLE Scan");

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true);
  pBLEScan->setInterval(100);
  pBLEScan->setWindow(99);
}

void loop() {
  unsigned long now = millis();
  if (now - lastScanTime > scanInterval) {
    Serial.println("[ESP32] Scanning...");
    pBLEScan->start(1, false);
    lastScanTime = now;
  }

  delay(50);
}
