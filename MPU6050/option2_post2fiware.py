import requests
import time
from datetime import datetime
from take_measurements import measure_average_acceleration
import threading 
from queue import Queue
import smbus
from getlocationandmodifyit import*

fiware_url = "http://150.140.186.118:1026/v2/entities"


serial_port = "/dev/ttyUSB2"
baud_rate=115200



# Headers for the request
headers = {
    "Content-Type": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics"
}

accum_queue = Queue()

def create_json(accx, accy, accz, gps_info):
    measurement = {
         "id": "IMU_Measurement",
         "type": "raw",

        "accx": {
            "value": accx,
            "type": "Number"
        },
        "accy": {
            "value": accy,
            "type": "Number"
        },
        "accz": {
            "value": accz,
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

def accum_measurements(duration=2, sample_interval=0.05):
    MPU6050_ADDR = 0x68
    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B

    # Initialize I2C bus
    bus = smbus.SMBus(1)
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)  # Wake up MPU6050

    # Function to read raw data
    def read_raw_data(addr):
        high = bus.read_byte_data(MPU6050_ADDR, addr)
        low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
        value = (high << 8) | low
        if value > 32768:
            value -= 65536
        return value

    # Infinite loop for continuous averaging
    while True:
        # Data lists to store readings
        accel_x_values = []
        accel_y_values = []
        accel_z_values = []

        start_time = time.time()

        # Collect data for the specified duration
        while time.time() - start_time < duration:
            accel_x = read_raw_data(ACCEL_XOUT_H)
            accel_y = read_raw_data(ACCEL_XOUT_H + 2)
            accel_z = read_raw_data(ACCEL_XOUT_H + 4)

            # Scale accelerometer readings
            ax = accel_x / 16384.0
            ay = accel_y / 16384.0
            az = accel_z / 16384.0


            print(f"Acceleration: {ax:.2f} g, {ay:.2f} g, {az:.2f} g")

            # Store values
            accel_x_values.append(ax)
            accel_y_values.append(ay)
            accel_z_values.append(az)

            time.sleep(sample_interval)

        # # Calculate averages
        # avg_ax = sum(accel_x_values) / len(accel_x_values)
        # avg_ay = sum(accel_y_values) / len(accel_y_values)
        # avg_az = sum(accel_z_values) / len(accel_z_values)
        # avg_acceleration = math.sqrt(avg_ax**2 + avg_ay**2 + avg_az**2)
        # print(f"Average acceleration: {avg_acceleration:.2f} g")

    
        return accel_x_values, accel_y_values, accel_z_values
def take_measurements():
    while True:
        accx, accy, accz = accum_measurements()
        gps_data=get_gps_location(serial_port, baud_rate)
        measurement = create_json(accx, accy, accz,gps_data)
        print(measurement)

        # Add the measurement to the queue
        accum_queue.put(measurement)
        #print(f"Measurement queued: {accx:.2f} g")


if __name__ == "__main__":
    try:
        measure_thread = threading.Thread(target=take_measurements,daemon=True)
        measure_thread.start()

        # Main loop: Post data to FIWARE when the queue is not empty
        while True:
            try:
                measurement = accum_queue.get(timeout=0.1)
            except: 
                measurement = None
            if measurement:
                post_to_fiware(measurement,fiware_url, headers)
                # patch_measurement(measurement,"http://150.140.186.118:1026/v2/entities/IMU_Measurement", headers)
                
                
                accum_queue.task_done()         # Mark the task as done

            else:
                time.sleep(0.1)  # Avoid busy waiting

    except KeyboardInterrupt:
        print("Program stopped by user.")
    
