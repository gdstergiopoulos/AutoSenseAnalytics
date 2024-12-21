import smbus
import numpy as np
from scipy.signal import butter, lfilter, welch
import time

# MPU6050 Registers
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

# Initialize I2C bus
bus = smbus.SMBus(1)

# Functions to interact with MPU6050
def read_word(adr):
    high = bus.read_byte_data(MPU6050_ADDR, adr)
    low = bus.read_byte_data(MPU6050_ADDR, adr + 1)
    val = (high << 8) + low
    if val >= 0x8000:
        return -((65535 - val) + 1)
    else:
        return val

def read_accel_data():
    accel_x = read_word(ACCEL_XOUT_H) / 16384.0
    accel_y = read_word(ACCEL_XOUT_H + 2) / 16384.0
    accel_z = read_word(ACCEL_XOUT_H + 4) / 16384.0
    return accel_x, accel_y, accel_z

# Low-pass filter
def butter_lowpass(cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def lowpass_filter(data, cutoff, fs, order=4):
    b, a = butter_lowpass(cutoff, fs, order=order)
    return lfilter(b, a, data)

# FFT processing
def process_fft(data, fs):
    fft_vals = np.fft.rfft(data)
    fft_freqs = np.fft.rfftfreq(len(data), 1 / fs)
    return fft_freqs, np.abs(fft_vals)

# Roughness metric (RMS)
def calculate_rms(data):
    return np.sqrt(np.mean(np.square(data)))

# Main function
if __name__ == "__main__":
    try:
        # Wake up MPU6050
        bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

        # Parameters
        sampling_rate = 50  # Hz
        window_duration = 2  # seconds
        cutoff_frequency = 20  # Hz (low-pass filter cutoff)
        
        window_size = int(sampling_rate * window_duration)
        accel_data_z = []

        print("Collecting data...")

        while True:
            start_time = time.time()

            # Collect data for the window
            for _ in range(window_size):
                _, _, accel_z = read_accel_data()
                accel_data_z.append(accel_z)
                time.sleep(1 / sampling_rate)

            # Apply low-pass filter
            filtered_data = lowpass_filter(accel_data_z, cutoff_frequency, sampling_rate)

            # FFT Processing
            freqs, fft_magnitudes = process_fft(filtered_data, sampling_rate)

            # Calculate roughness (RMS)
            rms = calculate_rms(filtered_data)

            # Detect anomalies based on threshold (adjust as needed)
            anomaly_threshold = 1.0  # Example threshold for RMS
            is_anomaly = rms > anomaly_threshold

            # Output results
            print(f"RMS: {rms:.2f}", "- Anomaly Detected!" if is_anomaly else "")

            # Optional: Save or send data to a service
            # ... (e.g., post to a server or save to file)

            # Clear data for the next window
            accel_data_z = []

            # Wait until the next window starts
            elapsed_time = time.time() - start_time
            time.sleep(max(0, window_duration - elapsed_time))

    except KeyboardInterrupt:
        print("Stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
