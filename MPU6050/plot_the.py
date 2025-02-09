import smbus
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# MPU6050 Registers and Addresses
MPU6050_ADDR = 0x68  # I2C address of the MPU6050
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

# Initialize I2C bus
bus = smbus.SMBus(1)  # Use bus 1 for Raspberry Pi

# Wake up the MPU6050 as it starts in sleep mode
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

# Function to read raw data
def read_raw_data(addr):
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

# Lists to store data
x_vals, y_vals, z_vals = [], [], []
time_vals = []

# Initialize plot
fig, ax = plt.subplots()
ax.set_ylim(-2, 2)  # Normalize acceleration range (-2g to +2g)
ax.set_xlim(0, 100)  # Show last 100 readings
ax.set_xlabel("Time")
ax.set_ylabel("Acceleration (g)")
ax.set_title("Real-Time MPU6050 Accelerometer Data")

# Create line objects
line_x, = ax.plot([], [], label="X-axis", color='r')
line_y, = ax.plot([], [], label="Y-axis", color='g')
line_z, = ax.plot([], [], label="Z-axis", color='b')

ax.legend()

# Update function for animation
def update(frame):
    global x_vals, y_vals, z_vals, time_vals
    
    # Read accelerometer raw values
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_XOUT_H + 2)
    acc_z = read_raw_data(ACCEL_XOUT_H + 4)

    # Convert raw values to 'g' force
    acc_x = acc_x / 16384.0
    acc_y = acc_y / 16384.0
    acc_z = acc_z / 16384.0

    # Append new values to lists
    time_vals.append(time.time())  # Timestamp
    x_vals.append(acc_x)
    y_vals.append(acc_y)
    z_vals.append(acc_z)

    # Keep only last 100 readings
    if len(time_vals) > 100:
        time_vals = time_vals[-100:]
        x_vals = x_vals[-100:]
        y_vals = y_vals[-100:]
        z_vals = z_vals[-100:]

    # Update plot data
    line_x.set_data(range(len(time_vals)), x_vals)
    line_y.set_data(range(len(time_vals)), y_vals)
    line_z.set_data(range(len(time_vals)), z_vals)
    
    return line_x, line_y, line_z

# Animate the plot
ani = animation.FuncAnimation(fig, update, interval=50, blit=False)

# Show the plot
plt.show()
