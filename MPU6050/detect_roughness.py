import smbus
import time
import math

# MPU6050 Registers and Address
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

# Initialize I2C
bus = smbus.SMBus(1)

# Wake up MPU6050 (exit sleep mode)
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

# Function to read raw 16-bit values διαβαζει τα δεδομενα απο δυο registers(ο καθενας 8 Bit) και τα μετατρεπει σε 16bit signed value
def read_raw_data(addr):
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

# Function to calculate acceleration magnitude
def calc_accel_magnitude(ax, ay, az):
    return math.sqrt(ax**2 + ay**2 + az**2)

# Thresholds for detecting anomalies
NORMAL_GRAVITY = 1.0  # Normal gravity (g-force)
ROUGHNESS_THRESHOLD = 0.4  # Change in g-force to detect roughness
DETECTION_WINDOW = 1  # Seconds to wait before next detection

print("Starting Road Roughness Detection... Press Ctrl+C to stop.")

try:
    while True:
        # Read accelerometer data καθε κατευθυνση εχει δικους τις registers
        accel_x = read_raw_data(ACCEL_XOUT_H)
        accel_y = read_raw_data(ACCEL_XOUT_H + 2)
        accel_z = read_raw_data(ACCEL_XOUT_H + 4)
        
        # Convert to g-force (assuming ±2g range) οι μετρησεις μας σε g-force μοναδα μετρησης: σε εναν σμουθ δρομο θα πρεπει να βγαινει 1g 
        ax = accel_x / 16384.0
        ay = accel_y / 16384.0
        az = accel_z / 16384.0
        
        # Calculate the acceleration magnitude
        accel_magnitude = calc_accel_magnitude(ax, ay, az)
        
        # Calculate the deviation from normal gravity
        deviation = abs(accel_magnitude - NORMAL_GRAVITY)
        
        # Check if deviation exceeds threshold
        if deviation > ROUGHNESS_THRESHOLD:
            print(f"Roughness Detected! Deviation: {deviation:.2f}g")
        else:
            print(f"Smooth Road - Deviation: {deviation:.2f}g")
        
        # Short delay to stabilize readings
        time.sleep(DETECTION_WINDOW)

except KeyboardInterrupt:
    print("Road Roughness Detection Stopped.")
