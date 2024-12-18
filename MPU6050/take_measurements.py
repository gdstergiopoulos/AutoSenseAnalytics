import time
import smbus
import math

def measure_average_acceleration(duration=2, sample_interval=0.2):
    # MPU6050 Registers and Addresses
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

        # Calculate averages
        avg_ax = sum(accel_x_values) / len(accel_x_values)
        avg_ay = sum(accel_y_values) / len(accel_y_values)
        avg_az = sum(accel_z_values) / len(accel_z_values)
        avg_acceleration = math.sqrt(avg_ax**2 + avg_ay**2 + avg_az**2)
        print(f"Average acceleration: {avg_acceleration:.2f} g")

    
        return avg_acceleration




# import smbus
# import time
# import math

# def measure_average_acceleration(duration=2, sample_interval=0.2):

#     # MPU6050 Registers and Addresses
#     MPU6050_ADDR = 0x68
#     PWR_MGMT_1 = 0x6B
#     ACCEL_XOUT_H = 0x3B

#     # Initialize I2C bus
#     bus = smbus.SMBus(1)

#     # Wake up MPU6050 (exit sleep mode)
#     bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

#     def read_raw_data(addr):
#         # Read two bytes of data
#         high = bus.read_byte_data(MPU6050_ADDR, addr)
#         low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
#         value = (high << 8) | low
#         # Convert to signed 16-bit value
#         if value > 32768:
#             value -= 65536
#         return value

#     # Data lists to store readings
#     accel_x_values = []
#     accel_y_values = []
#     accel_z_values = []

#     start_time = time.time()
    
#     while True:
#         # Read accelerometer data
#         accel_x = read_raw_data(ACCEL_XOUT_H)
#         accel_y = read_raw_data(ACCEL_XOUT_H + 2)
#         accel_z = read_raw_data(ACCEL_XOUT_H + 4)
        
#         # Scale accelerometer readings (assuming 2g range)
#         ax = accel_x / 16384.0
#         ay = accel_y / 16384.0
#         az = accel_z / 16384.0
#         # print(ax, ay, az)       
        
#         # Store values in lists
#         accel_x_values.append(ax)
#         accel_y_values.append(ay)
#         accel_z_values.append(az)
        
#         # Check if the duration is reached
#         elapsed_time = time.time() - start_time
#         if elapsed_time >= duration:
#             # Calculate averages
#             avg_ax = sum(accel_x_values) / len(accel_x_values)
#             avg_ay = sum(accel_y_values) / len(accel_y_values)
#             avg_az = sum(accel_z_values) / len(accel_z_values)
            
#             # Calculate average acceleration
#             avg_acceleration = math.sqrt(avg_ax**2 + avg_ay**2 + avg_az**2)
            
#             # Clear lists for next calculation
#             accel_x_values.clear()
#             accel_y_values.clear()
#             accel_z_values.clear()
            
#             return avg_acceleration
        
#         time.sleep(sample_interval)


# try:
#     while True:
#         avg_acceleration = measure_average_acceleration()
#         print(f"Average Acceleration: {avg_acceleration:.2f} g")
# except KeyboardInterrupt:
#     print("Measurement stopped.")
