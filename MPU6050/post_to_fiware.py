import requests
import time
from datetime import datetime
from take_measurements import measure_average_acceleration
import threading 
from queue import Queue
#from get_location_without_class import fetch_gps_data     !!!!!!!!!!!!!!!!!!!!!!!!! no gps and mpu available at the same time



fiware_url = "http://150.140.186.118:1026/v2/entities"

average_queue = Queue()


# Headers for the request
headers = {
    "Content-Type": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics"
}


def create_json(acc, timestamp, location):
    measurement = {
        "acceleration": {
            "value": acc,
            "type": "Number"
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
    return 0


# Patch the measurement to FIWARE
def patch_measurement( measurement,fiware_url=fiware_url, headers=headers):
    try:
        response = requests.patch(fiware_url, headers=headers, json=measurement)
        response.raise_for_status()
        print("Measurement patched successfully.")
    except requests.exceptions.HTTPError as err:
        print(f"Failed to patch measurement: {err}")

    return 0



# Thread 1: Continuously measure and calculate average acceleration
def measure_average():
    while True:
        avg_acceleration = measure_average_acceleration()  # Calculate the average
        print("This is after")
        print(avg_acceleration)
        timestamp = datetime.now().isoformat()
        location=[21.753150, 38.230462]
        measurement = create_json(avg_acceleration, timestamp, location)
        print(measurement)

        # Add the measurement to the queue
        average_queue.put(measurement)
        print(f"Average acceleration queued: {avg_acceleration:.2f} g")




if __name__ == "__main__":
    try:
        measure_thread = threading.Thread(target=measure_average,daemon=True)
        measure_thread.start()

        # Main loop: Post data to FIWARE when the queue is not empty
        while True:
            try:
                measurement = average_queue.get(timeout=0.1)
            except: 
                measurement = None
            if measurement:
                patch_measurement(measurement,fiware_url+"/MPU_Measurement/attrs", headers)
                average_queue.task_done()         # Mark the task as done

            else:
                time.sleep(0.1)  # Avoid busy waiting

    except KeyboardInterrupt:
        print("Program stopped by user.")



















# def wifi_measurement_loop(interval=10):
#     #post_to_fiware(testmeasurement,fiware_url=fiware_url, headers=headers) 
#     #change if you want to change the service path
#     failed=False
#     while True:
#         bssid, rssi,timestamp = get_wifi_measurement()
#         location=fetch_gps_data()
#         print(f"BSSID: {bssid}, RSSI: {rssi} dBm, Timestamp: {timestamp}, Location: {location}")
#         currmeasure = create_json(bssid, rssi, timestamp, location)
#         print(currmeasure)
#         if currmeasure:
#             try:
#                 if failed:
#                     cursor = connect.cursor()
#                     cursor.execute("SELECT bssid, rssi, timestamp, location FROM wifi")
#                     cached_measurements = cursor.fetchall()
#                     print(cached_measurements)
#                     for cached_measurement in cached_measurements:
#                         cached_bssid, cached_rssi, cached_timestamp, cached_location = cached_measurement
#                         cached_json = create_json(cached_bssid, cached_rssi, cached_timestamp,ast.literal_eval(cached_location))
#                         print(cached_json)
#                         try:
#                             patch_measument(cached_json, fiware_url + "/elenishome/attrs", headers)
#                             cursor.execute("DELETE FROM wifi WHERE bssid = ? AND timestamp = ?", (cached_bssid, cached_timestamp))
#                             print("Cached deleted "+cached_timestamp)
#                             connect.commit()
#                         except requests.exceptions.HTTPError as err:
#                             print(f"Failed to patch cached measurement: {err}")
#                     cursor.close()
#                     failed=False
#                 patch_measument(currmeasure, fiware_url + "/elenishome/attrs", headers)
#             except:
#                 print("Failed to patch measurement")
#                 failed=True
#                 cursor = connect.cursor()
#                 cursor.execute("INSERT INTO wifi (bssid, rssi, timestamp, location,area) VALUES (?, ?, ?, ?,?)", 
#                            (bssid, rssi, timestamp, str(location),"kypestest"))
#                 connect.commit()
#                 cursor.close()
#         else:
#             print("No WiFi connection detected.")
            
#         time.sleep(interval)
    


