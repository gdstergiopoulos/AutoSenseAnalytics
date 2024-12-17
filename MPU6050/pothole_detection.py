
# ΜΟΝΟ ΑΝ ΠΑΜΕ ΣΥΓΚΕΚΡΙΜΕΝΑ ΓΙΑ ΛΑΚΟΥΒΕΣ !!! ΑΛΛΑΖΕΙ το range στο  g και κραταμε τον αξονα z 


import smbus
import time

# MPU6050 Registers and Address
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
ACCEL_CONFIG = 0x1C

# Initialize I2C bus
bus = smbus.SMBus(1)

# Wake up MPU6050
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

# Set accelerometer to ±4g for pothole detection
bus.write_byte_data(MPU6050_ADDR, ACCEL_CONFIG, 0x08)
print("MPU6050 Initialized: Accelerometer set to ±4g range.")

# Function to read raw data
def read_raw_data(addr):
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

try:
    while True:
        # Read accelerometer raw values
        accel_z = read_raw_data(ACCEL_XOUT_H + 4)  # Z-axis

        # Convert to g-force (±4g mode, sensitivity = 8192 LSB/g)
        az = accel_z / 8192.0

        # Check if Z-axis drops below threshold
        if az < 0.7:  # Adjust threshold as needed
            print(f"Pothole Detected! Z-axis: {az:.2f}g")
        else:
            print(f"Smooth Road - Z-axis: {az:.2f}g")

        time.sleep(0.1)  # Check every 100ms

except KeyboardInterrupt:
    print("Pothole detection stopped.")
