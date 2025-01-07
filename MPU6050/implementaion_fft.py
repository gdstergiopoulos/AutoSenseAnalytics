import time
import smbus
import math
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import butter, filtfilt


# MPU6050 Data Collection
def collect_acceleration_data(duration=2, sample_interval=0.01):
    """
    Collect acceleration data from the MPU6050 at a specified sampling interval.
    Args:
        duration: Total time to collect data in seconds (default is 2 seconds).
        sample_interval: Time between consecutive samples in seconds (default is 0.01 seconds for 100 Hz).
    Returns:
        List of total acceleration magnitudes over the duration.
    """
    MPU6050_ADDR = 0x68
    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B

    # Initialize the MPU6050 via I2C
    bus = smbus.SMBus(1)
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)  # Wake up the MPU6050

    # Function to read raw data from the sensor
    def read_raw_data(addr):
        high = bus.read_byte_data(MPU6050_ADDR, addr)
        low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
        value = (high << 8) | low
        if value > 32768:  # Convert to signed value
            value -= 65536
        return value

    acceleration_data = []
    start_time = time.time()

    # Collect data for the specified duration
    while time.time() - start_time < duration:
        accel_x = read_raw_data(ACCEL_XOUT_H)
        accel_y = read_raw_data(ACCEL_XOUT_H + 2)
        accel_z = read_raw_data(ACCEL_XOUT_H + 4)

        # Convert raw values to acceleration in g
        ax = accel_x / 16384.0
        ay = accel_y / 16384.0
        az = accel_z / 16384.0

        # Calculate total acceleration magnitude
        total_acceleration = math.sqrt(ax**2 + ay**2 + az**2)
        acceleration_data.append(total_acceleration)

        # Adjust timing to maintain precise sampling intervals
        next_sample_time = start_time + len(acceleration_data) * sample_interval
        time.sleep(max(0, next_sample_time - time.time()))

    return acceleration_data


# Bandpass Filter
def bandpass_filter(data, lowcut, highcut, fs, order=4):
    """
    Apply a bandpass Butterworth filter to the input data.
    Args:
        data: List or NumPy array of raw acceleration data.
        lowcut: Low cutoff frequency in Hz.
        highcut: High cutoff frequency in Hz.
        fs: Sampling frequency in Hz.
        order: Filter order (default is 4).
    Returns:
        Filtered data as a NumPy array.
    """
    nyquist = 0.5 * fs  # Nyquist frequency
    low = lowcut / nyquist
    high = highcut / nyquist

    # Ensure frequencies are within valid range
    if not (0 < low < high < 1):
        raise ValueError(f"Critical frequencies must satisfy 0 < low < high < 1. Given: low={low}, high={high}")

    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)


# FFT and Filtering
def process_fft_and_filter(data, fs):
    """
    Perform FFT and apply a bandpass filter to the input data.
    Args:
        data: List or NumPy array of raw acceleration data.
        fs: Sampling frequency in Hz.
    Returns:
        Average acceleration value after processing.
    """
    if len(data) < 10:  # Ensure enough data for FFT and filtering
        raise ValueError("Insufficient data for processing.")

    # Apply FFT
    n = len(data)
    fft_values = fft(data)
    frequencies = fftfreq(n, d=1/fs)

    # Use only positive frequencies
    positive_frequencies = frequencies[frequencies >= 0]
    relevant_indices = (positive_frequencies >= 5) & (positive_frequencies <= 50)

    # Debugging: Print FFT results (optional)
    # print(f"Relevant Frequencies: {positive_frequencies[relevant_indices]}")
    # print(f"FFT Magnitudes: {np.abs(fft_values[relevant_indices])}")

    # Apply bandpass filter
    filtered_data = bandpass_filter(data, lowcut=5, highcut=49, fs=fs)

    # Take the absolute value of the filtered signal
    absolute_data = np.abs(filtered_data)

    # Calculate average acceleration
    avg_acceleration = np.mean(absolute_data)

    return avg_acceleration


# Main Program
if __name__ == "__main__":
    fs = 100  # Sampling frequency in Hz (100 Hz)
    duration = 2  # Duration for data collection in seconds

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
