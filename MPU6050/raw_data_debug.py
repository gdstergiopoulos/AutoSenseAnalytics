import smbus
import time

MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

bus = smbus.SMBus(1)

bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

# Function to read raw 16-bit values διαβαζει τα δεδομενα απο δυο registers(ο καθενας 8 Bit) και τα μετατρεπει σε 16bit signed value
def read_raw_data(addr):
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value




def save_to_file(ax, ay, az, filename="RawData.txt"):
    try:
        with open(filename, "a") as file:  
            file.write(f"{ax},{ay},{az}\n")  
    except Exception as e:
        print(f"Error writing to file {filename}: {e}")



try:
    while True:
        # Read accelerometer data καθε κατευθυνση εχει δικους τις registers
        accel_x = read_raw_data(ACCEL_XOUT_H)
        accel_y = read_raw_data(ACCEL_XOUT_H + 2)
        accel_z = read_raw_data(ACCEL_XOUT_H + 4)
        
        ax = accel_x / 16384.0
        ay = accel_y / 16384.0
        az = accel_z / 16384.0


        save_to_file(ax, ay, az)

        time.sleep(0.01)

     
except KeyboardInterrupt:
    print("Road Roughness Detection Stopped.")
