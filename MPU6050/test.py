import smbus
import time

# MPU6050 Registers and Addresses
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

# Initialize I2C bus
bus = smbus.SMBus(1)

# Wake up MPU6050 (exit sleep mode)
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

def read_raw_data(addr):
    # Read two bytes of data
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    value = (high << 8) | low
    # Convert to signed 16-bit value
    if value > 32768:
        value -= 65536
    return value

try:
    while True:
        # Read accelerometer data
        accel_x = read_raw_data(ACCEL_XOUT_H)
        accel_y = read_raw_data(ACCEL_XOUT_H + 2)
        accel_z = read_raw_data(ACCEL_XOUT_H + 4)
        
        # Scale accelerometer readings (assuming 2g range)
        ax = accel_x / 16384.0
        ay = accel_y / 16384.0
        az = accel_z / 16384.0
        
        print(f"Ax: {ax:.2f} g, Ay: {ay:.2f} g, Az: {az:.2f} g")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Measurement stopped.")
