import time
import smbus
import math

def measure_average_acceleration(duration=2, sample_interval=0.2):
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

        avg_ax = sum(accel_x_values) / len(accel_x_values)
        avg_ay = sum(accel_y_values) / len(accel_y_values)
        avg_az = sum(accel_z_values) / len(accel_z_values)
        avg_acceleration = math.sqrt(avg_ax**2 + avg_ay**2 + avg_az**2)
        print(f"Average acceleration: {avg_acceleration:.2f} g")

    
        return avg_acceleration