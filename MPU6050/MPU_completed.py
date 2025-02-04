import requests
import time
from datetime import datetime
from implementaion_fft import *
import threading 
from queue import Queue
from getlocationandmodifyit import* 

serial_port = "/dev/ttyUSB2"
baud_rate=115200


fiware_url = "http://150.140.186.118:1026/v2/entities"

average_queue = Queue()


headers = {
    "Content-Type": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics"
}


def create_json(acc, gps_info):
    measurement = {
        # "id": "MPU_Measurement", for posting to FIWARE only
        # "type": "acc",

        "acceleration": {
            "value": acc,
            "type": "Number"
        },
         "location": {
            "value": {
                "type": "Point",
                "coordinates": [gps_info.get("latitude"), gps_info.get("longitude")]
            },
            "type": "geo:json"
        },
        "date": {
            "value": gps_info.get("date"),
            "type": "DateTime"
        },
        "altitude": {
            "value": gps_info.get("altitude"),
            "type": "Number"
        },
        "speed": {
            "value": gps_info.get("speed"),
            "type": "Number"
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
        try:
            avg_acceleration = get_acceleration(100,1)  # Calculate the average
            print("This is after")
            print(avg_acceleration)
            if avg_acceleration:
                gps_info=get_gps_location(serial_port, baud_rate)

                measurement = create_json(avg_acceleration,gps_info)
                print(measurement)

                average_queue.put(measurement)
                print(f"Average acceleration queued: {avg_acceleration:.2f} g")
        except KeyboardInterrupt:
            print("Measurement stopped by user.")
            break




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
                # post_to_fiware(measurement,fiware_url, headers)
                patch_measurement(measurement,fiware_url+"/MPU_Measurement/attrs", headers)
                average_queue.task_done()         # Mark the task as done

            else:
                time.sleep(0.1)  # Avoid busy waiting

    except KeyboardInterrupt:
        print("Program stopped by user.")









