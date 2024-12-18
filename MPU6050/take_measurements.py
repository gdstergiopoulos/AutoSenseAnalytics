import smbus
import time
import math

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

# Data lists to store readings
accel_x_values = []
accel_y_values = []
accel_z_values = []

try:
    start_time = time.time()
    while True:
        # Read accelerometer data
        accel_x = read_raw_data(ACCEL_XOUT_H)
        accel_y = read_raw_data(ACCEL_XOUT_H + 2)
        accel_z = read_raw_data(ACCEL_XOUT_H + 4)
        
        # Scale accelerometer readings (assuming 2g range)
        ax = accel_x / 16384.0
        ay = accel_y / 16384.0
        az = accel_z / 16384.0
        
        # Store values in lists
        accel_x_values.append(ax)
        accel_y_values.append(ay)
        accel_z_values.append(az)
        
        print(f"Ax: {ax:.2f} g, Ay: {ay:.2f} g, Az: {az:.2f} g")
        
        # Every 2 seconds, calculate averages
        elapsed_time = time.time() - start_time
        if elapsed_time >= 2:  # 2 seconds
            # Calculate averages
            #print(accel_x_values)
            avg_ax = sum(accel_x_values) / len(accel_x_values)
            avg_ay = sum(accel_y_values) / len(accel_y_values)
            avg_az = sum(accel_z_values) / len(accel_z_values)
            
            # Calculate average acceleration
            avg_acceleration = math.sqrt(avg_ax**2 + avg_ay**2 + avg_az**2)
            
            print("\n--- Averages over the last 2 seconds ---")
            print(f"Avg Ax: {avg_ax:.2f} g, Avg Ay: {avg_ay:.2f} g, Avg Az: {avg_az:.2f} g")
            print(f"Avg Total Acceleration: {avg_acceleration:.2f} g\n")
            
            # Remove the averaged values from the lists
            accel_x_values.clear()
            accel_y_values.clear()
            accel_z_values.clear()
            
            # Reset the timer for the next interval
            start_time = time.time()
        
        time.sleep(0.2)  # Measure every 0.2 seconds

except KeyboardInterrupt:
    print("Measurement stopped.")
