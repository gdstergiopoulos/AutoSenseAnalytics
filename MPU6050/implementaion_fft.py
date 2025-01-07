import time
import smbus
import math
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import butter, filtfilt


# MPU6050 Data Collection
def collect_acceleration_data(duration=2, sample_interval=0.01):
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

    acceleration_data = []
    start_time = time.time()

    while time.time() - start_time < duration:
        accel_x = read_raw_data(ACCEL_XOUT_H)
        accel_y = read_raw_data(ACCEL_XOUT_H + 2)
        accel_z = read_raw_data(ACCEL_XOUT_H + 4)

        ax = accel_x / 16384.0
        ay = accel_y / 16384.0
        az = accel_z / 16384.0

        total_acceleration = math.sqrt(ax**2 + ay**2 + az**2)
        print(total_acceleration)
        acceleration_data.append(total_acceleration)

        time.sleep(sample_interval)

    return acceleration_data


def bandpass_filter(data, lowcut, highcut, fs, order=4):

    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)


def process_fft_and_filter(data, fs):

    # Apply FFT
    n = len(data)
    fft_values = fft(data)
    frequencies = fftfreq(n, d=1/fs)

    relevant_indices = (frequencies >= 5) & (frequencies <= 50)

    filtered_data = bandpass_filter(data, lowcut=5, highcut=50, fs=fs)

    # Take absolute value of the filtered signal
    absolute_data = np.abs(filtered_data)

    # Calculate average acceleration
    avg_acceleration = np.mean(absolute_data)

    return avg_acceleration


# Main Program
if __name__ == "__main__":
    fs = 100  # Sampling frequency (100 Hz)
    duration = 2  # Collect data for 2 seconds

    try:
        print("Collecting data from MPU6050...")
        raw_acceleration_data = collect_acceleration_data(duration, sample_interval=1/fs)

        print("Processing data...")
        final_avg_acceleration = process_fft_and_filter(raw_acceleration_data, fs)

        print(f"Final average acceleration after filtering: {final_avg_acceleration:.2f} g")

    except KeyboardInterrupt:
        print("Program stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
