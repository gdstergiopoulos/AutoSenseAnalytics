import requests
import datetime


fiware_url = "http://150.140.186.118:1026/v2/entities/elenishome/attrs"  # Replace with your entity ID

# Headers for the request
headers = {
    "Content-Type": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics/Wifi" # Different-path including Project Wifi
}

measurement = {
        "rssi": {
            "value": -47,
            "type": "Number"
        },
        "macAddress": {
            "value": "00:11:22:33:44:55",
            "type": "Text"
        },
        "location": {
            "value": {
                "type": "Point",
                "coordinates": [21.75315,38.230462]
            },
            "type": "geo:json"
        },
        "timestamp": {
            "value":  datetime.datetime.now().isoformat(),
            "type": "DateTime"
        }
    }

def patch_measument( measurement,fiware_url=fiware_url, headers=headers): #for uploading the measurements
    try:
        response = requests.patch(fiware_url, headers=headers, json=measurement)
        response.raise_for_status()
        print("Measurement patched successfully.")
    except requests.exceptions.HTTPError as err:
        print(f"Failed to patch measurement: {err}")

    return 0

patch_measument(measurement)