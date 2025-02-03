import smbus
import time

def get_acceleration():
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

    accel_x = read_raw_data(ACCEL_XOUT_H)
    accel_y = read_raw_data(ACCEL_XOUT_H + 2)
    accel_z = read_raw_data(ACCEL_XOUT_H + 4)

    ax = accel_x / 16384.0
    ay = accel_y / 16384.0
    az = accel_z / 16384.0

    print(f"Instant Acceleration: ax={ax:.2f} g, ay={ay:.2f} g, az={az:.2f} g")

    return ax, ay, az

# get_acceleration()