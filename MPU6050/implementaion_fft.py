import time
import smbus
import math
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import butter, filtfilt
from getlocationfrom4Ghat import get_gps_location



serial_port = "/dev/ttyUSB2"  
baud_rate = 115200



def collect_acceleration_data(duration, sample_interval=0.01):
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

        next_sample_time = start_time + len(acceleration_data) * sample_interval
        time.sleep(max(0, next_sample_time - time.time()))

    return acceleration_data


def bandpass_filter(data, fs, lowcut=5, highcut=49,  order=4):
    nyquist = 0.5 * fs  # Nyquist frequency
    low = lowcut / nyquist
    high = highcut / nyquist

    if not (0 < low < high < 1):
        raise ValueError(f"Critical frequencies must satisfy 0 < low < high < 1. Given: low={low}, high={high}")

    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)

def process_fft_and_filter(data, fs):

    if len(data) < 10:  
        raise ValueError("Insufficient data for processing.")

    # Apply FFT
    n = len(data)
    fft_values = fft(data)  
    frequencies = fftfreq(n, d=1/fs)  

    fft_magnitudes = np.abs(fft_values)

    # print("Frequencies:", frequencies)
    # print("FFT Magnitudes:", fft_magnitudes)

    filtered_data = bandpass_filter(data,fs=fs, lowcut=5, highcut=49, )

    absolute_data = np.abs(filtered_data)

    avg_acceleration = np.mean(absolute_data)

    return avg_acceleration


if __name__ == "__main__":
    fs = 100  #100 samples in one second 
    duration = 1

    try:
        while True:
            print("Collecting data from MPU6050...")
            raw_acceleration_data = collect_acceleration_data(duration, sample_interval=1/fs)

            print("Processing data...")
            final_avg_acceleration = process_fft_and_filter(raw_acceleration_data, fs)
            if final_avg_acceleration:
                gps_location = get_gps_location(serial_port, baud_rate)

            print(f"Final average acceleration after filtering: {final_avg_acceleration:.2f} g")
            print(gps_location)

    except KeyboardInterrupt:
        print("Program stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
