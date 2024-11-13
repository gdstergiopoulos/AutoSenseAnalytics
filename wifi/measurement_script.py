import requests
import time
from datetime import datetime
from SCRIPT_rssi_bssd_single import get_wifi_measurement
# FIWARE Orion Context Broker URL
fiware_url = "http://150.140.186.118:1026/v2/entities"

# Fake measurement data
testmeasurement = {
    "id": "WiFiMeasurement",
    "type": "rssi_bssid",
    "rssi": {
        "value": -45,
        "type": "Number"
    },
    "macAddress": {
        "value": "00:14:22:01:23:45",
        "type": "Text"
    },
    "location": {
        "value": {
            "type": "Point",
            "coordinates": [21.753150, 38.230462]
        },
        "type": "geo:json"
    },
    "timestamp": {
        "value": datetime.now().isoformat(),
        "type": "DateTime"
    }
}

# Headers for the request
headers = {
    "Content-Type": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics"
}


def create_json(bssid, rssi, timestamp, location):
    measurement = {
        "rssi": {
            "value": rssi,
            "type": "Number"
        },
        "macAddress": {
            "value": bssid,
            "type": "Text"
        },
        "location": {
            "value": {
                "type": "Point",
                "coordinates": location
            },
            "type": "geo:json"
        },
        "timestamp": {
            "value": timestamp,
            "type": "DateTime"
        }
    }
    return measurement

# Post the measurement to FIWARE
def post_to_fiware(measurement,fiware_url=fiware_url, headers=headers):
    try:
        response = requests.post(fiware_url, headers=headers, json=measurement)
        response.raise_for_status()
        print("Measurement posted successfully.")
    except requests.exceptions.HTTPError as err:
        print(f"Failed to post measurement: {err}")

    # response = requests.post(fiware_url, headers=headers, json=measurement)

    # Check the response
    # if response.status_code == 201:
    #     print("Measurement posted successfully.")
    # else:
    #     print(f"Failed to post measurement. Status code: {response.status_code}, Response: {response.text}")
    return 0

def patch_measument( measurement,fiware_url=fiware_url, headers=headers):
    try:
        response = requests.patch(fiware_url, headers=headers, json=measurement)
        response.raise_for_status()
        print("Measurement patched successfully.")
    except requests.exceptions.HTTPError as err:
        print(f"Failed to patch measurement: {err}")

    return 0

def wifi_measurement_loop(interval=10):
    #post_to_fiware(fiware_url=fiware_url, headers=headers, measurement=measurement) 
    #change if you want to change the service path
    while True:
        bssid, rssi,timestamp,location = get_wifi_measurement()

        print(f"BSSID: {bssid}, RSSI: {rssi} dBm, Timestamp: {timestamp}")
        # currmeasure = create_json(bssid, rssi, timestamp, location)
        currmeasure = {
            "rssi": {
                "value": rssi,
                "type": "Number"
            },
            "macAddress": {
                "value": bssid,
                "type": "Text"
            },
            "location": {
                "value": {
                    "type": "Point",
                    "coordinates": location
                },
                "type": "geo:json"
            },
            "timestamp": {
                "value": timestamp,
                "type": "DateTime"
            }
        }
        if currmeasure:
            patch_measument(currmeasure,fiware_url+"/WiFiMeasurement/attrs", headers)
        else:
            print("No WiFi connection detected.")

        time.sleep(interval)
    


#patch_measument(fiware_url=fiware_url+"/WiFiMeasurement/attrs", headers=headers, measurement=measurement2)

wifi_measurement_loop(10)