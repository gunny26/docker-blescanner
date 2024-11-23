#!/usr/bin/python3
import asyncio
import logging
import os
import time

# custom modules
import yaml
from bleak import BleakScanner
from prometheus_client import start_http_server, Counter, Summary

EXPORTER_INTERVAL = int(
    os.environ.get("APP_INTERVAL", "20")
)  # interval in seconds to do the sync
EXPORTER_LOG_LEVEL = os.environ.get("EXPORTER_LOG_LEVEL", "INFO")
EXPORTER_PORT = int(os.environ.get("EXPORTER_PORT", "9100"))

# setting Logging
if EXPORTER_LOG_LEVEL == "INFO":
    logging.getLogger().setLevel(logging.INFO)

if EXPORTER_LOG_LEVEL == "ERROR":
    logging.getLogger().setLevel(logging.ERROR)

if EXPORTER_LOG_LEVEL == "DEBUG":
    logging.getLogger().setLevel(logging.DEBUG)

# prometheus metrics
SUMMARY = Summary("blescanner_processing_seconds", "Time spent processing a scan")
DEVICE_SEEN_TOTAL = Counter(
    "blescanner_seen_total",
    "Number of intervals this devices was seen",
    ["address", "name"],
)

DEVICES = {}  # just for internal use

# typical BLE Device Data returned by discovery
"""
address: 40:7C:E4:AE:40:16
details:
  path: /org/bluez/hci0/dev_40_7C_E4_AE_40_16
  props:
    Adapter: /org/bluez/hci0
    Address: 40:7C:E4:AE:40:16
    AddressType: random
    Alias: 40-7C-E4-AE-40-16
    Blocked: false
    Connected: false
    LegacyPairing: false
    ManufacturerData:
      76: !!python/object/apply:builtins.bytearray
      - "\x16\b\0\x93'\xdb\xc5\x17\x01\x05"
      - latin-1
    Paired: false
    RSSI: -92
    ServicesResolved: false
    Trusted: false
    UUIDs: []
first_seen: 1730587116.0427468
last_seen: 1730587116.042747
name: 40-7C-E4-AE-40-16
seen: 1
"""


@SUMMARY.time()
async def main():
    devices = await BleakScanner.discover()
    for d in devices:
        logging.debug(d.address)
        logging.debug(d.name)
        logging.debug(d.details)
        if d.details["props"]["AddressType"] == "random":  # ignoring random addresses
            logging.info(f"Ignoring {d.address}, this is a RandomAddress")
            continue
        DEVICE_SEEN_TOTAL.labels(
            address=d.address, name=d.name
        ).inc()  # increment up if device was seen

        if d.address not in DEVICES:
            logging.info(f"New BLE device with address {d.address} detected")
            DEVICES[d.address] = {
                "address": d.address,
                "name": d.name,
                "details": d.details,
                "first_seen": time.time(),
                "last_seen": time.time(),
                "seen": 1,
            }
            logging.debug(yaml.dump(DEVICES[d.address], indent=2))
        else:
            logging.info(f"BLE device with address {d.address} updated")
            DEVICES[d.address]["last_seen"] = time.time()
            DEVICES[d.address]["seen"] += 1


if __name__ == "__main__":
    logging.info(f"starting prometheus exporter on port {EXPORTER_PORT}")
    start_http_server(EXPORTER_PORT)  # start prometheus exporter on port 9000/tcp
    while True:  # start endloess loop to scan ever INTERVALS seconds
        try:
            asyncio.run(main())
        except Exception as exc:
            logging.error("Some Exception while scanning")
            logging.exception(exc)
        # just for INFO
        for key, value in sorted(
            DEVICES.items(), key=lambda item: item[1]["last_seen"], reverse=True
        ):
            logging.info(f"{key}\t{value['last_seen']}\t{value['seen']}")
        logging.info(f"found in total {len(DEVICES)} BLE devices")
        time.sleep(EXPORTER_INTERVAL)
