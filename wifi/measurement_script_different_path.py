import requests
import time
from datetime import datetime
from SCRIPT_rssi_bssd_single import get_wifi_measurement
import sqlite3

# FIWARE Orion Context Broker URL
fiware_url = "http://150.140.186.118:1026/v2/entities"
connect=sqlite3.connect('./wifi/cache_measurements.sqlite')

# Headers for the request
headers = {
    "Content-Type": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics/Wifi" # Different-path including Project Wifi
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

# Post the measurement to FIWARE only once at the creation of the path 
def post_to_fiware(measurement,fiware_url=fiware_url, headers=headers):
    try:
        response = requests.post(fiware_url, headers=headers, json=measurement)
        response.raise_for_status()
        print("Measurement posted successfully.")
    except requests.exceptions.HTTPError as err:
        print(f"Failed to post measurement: {err}")

    return 0

def patch_measument( measurement,fiware_url=fiware_url, headers=headers): #for uploading the measurements
    try:
        response = requests.patch(fiware_url, headers=headers, json=measurement)
        response.raise_for_status()
        print("Measurement patched successfully.")
    except requests.exceptions.HTTPError as err:
        print(f"Failed to patch measurement: {err}")

    return 0

def wifi_measurement_loop(interval=10):
    #post_to_fiware(testmeasurement,fiware_url=fiware_url, headers=headers) 
    #change if you want to change the service path
    while True:
        bssid, rssi,timestamp,location = get_wifi_measurement()

        print(f"BSSID: {bssid}, RSSI: {rssi} dBm, Timestamp: {timestamp}")
        currmeasure = create_json(bssid, rssi, timestamp, location)
        if currmeasure:
            try:
                patch_measument(currmeasure,fiware_url+"/elenishome/attrs", headers)
            except:
                print("Failed to patch measurement")
                cursor = connect.cursor()
                cursor.execute("INSERT INTO wifi (bssid, rssi, timestamp, location,area) VALUES (?, ?, ?, ?,?)", 
                           (bssid, rssi, timestamp, str(location),"kypestest"))
                connect.commit()
                cursor.close()
        else:
            print("No WiFi connection detected.")
            
        time.sleep(interval)
    


wifi_measurement_loop(10)