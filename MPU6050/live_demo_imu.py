import time
import smbus
import math
from datetime import datetime
import requests


fiware_url = "http://150.140.186.118:1026/v2/entities"

headers = {
    "Content-Type": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics"
}



def post_to_fiware(measurement,fiware_url=fiware_url, headers=headers):
    try:
        response = requests.post(fiware_url, headers=headers, json=measurement)
        response.raise_for_status()
        print("Measurement posted successfully.")
    except requests.exceptions.HTTPError as err:
        print(f"Failed to post measurement: {err}")
    return 0



def patch_measurement( measurement,fiware_url=fiware_url, headers=headers):
    try:
        response = requests.patch(fiware_url, headers=headers, json=measurement)
        response.raise_for_status()
        print("Measurement patched successfully.")
        
    except requests.exceptions.HTTPError as err:
        print(f"Failed to patch measurement: {err}")
        

    return 0




def create_json(accx, accy ,accz, accavg):
    measurement = {
        "id": "IMU_avg", 
         "type": "Demo",

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
        "acc_avg": {
            "value": accavg,
            "type": "Number"
        },
        "timestamp": {
            "value": datetime.now().isoformat(),
            "type": "DateTime"
    }}
    return measurement
    




def measure_average_acceleration(duration=1, sample_interval=0.2):
    MPU6050_ADDR = 0x68
    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B

    bus = smbus.SMBus(1)
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)  

    def read_raw_data(addr):
        high = bus.read_byte_data(MPU6050_ADDR, addr)
        low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
        value = (high << 8) | low
        if value > 32768:
            value -= 65536
        return value

    while True:
        accel_x_values = []
        accel_y_values = []
        accel_z_values = []

        start_time = time.time()

        while time.time() - start_time < duration:
            accel_x = read_raw_data(ACCEL_XOUT_H)
            accel_y = read_raw_data(ACCEL_XOUT_H + 2)
            accel_z = read_raw_data(ACCEL_XOUT_H + 4)

            ax = accel_x / 16384.0
            ay = accel_y / 16384.0
            az = accel_z / 16384.0


            print(f"Acceleration: {ax:.2f} g, {ay:.2f} g, {az:.2f} g")

            accel_x_values.append(ax)
            accel_y_values.append(ay)
            accel_z_values.append(az)

            time.sleep(sample_interval)

        avg_x = sum(accel_x_values) / len(accel_x_values)
        avg_y = sum(accel_y_values) / len(accel_y_values)
        avg_z = sum(accel_z_values) / len(accel_z_values)
        avg_acceleration = math.sqrt(avg_x**2 + avg_y**2 + avg_z**2)
        # print(f"Average acceleration: {avg_acceleration:.2f} g")

    
        return avg_x, avg_y, avg_z, avg_acceleration
    




if __name__ == "__main__":
        try:
            while True:

                avg_x, avg_y, avg_z, avg_acceleration = measure_average_acceleration(1, 0.1)
                # print(avg_x, avg_y, avg_z, avg_acceleration)
                measurement = create_json(avg_x, avg_y, avg_z, avg_acceleration)
                # print(measurement)
                post_to_fiware(measurement,fiware_url, headers)
                patch_measurement(measurement,fiware_url+"/IMU_avg/attrs", headers)

        except KeyboardInterrupt:
            print("Measurement Error.")   