from datetime import datetime
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import butter, filtfilt

import mysql.connector

db_config = {
    'host': '150.140.186.118',
    'port': 3306,
    'user': 'readonly_student',
    'password': 'iot_password',
    'database': 'default'
}

def fetch_data(table_name, attr_name, start_datetime=None, end_datetime=None):
    
    try:
        # Establish the connection to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = f"""
            SELECT recvTime,attrValue
            FROM `default`.AutoSenseAnalytics_MPU_Measurement_acc
            WHERE recvTime>"2024-12-21 18:24:01.545" AND attrName="acceleration";;
        """
        
        # Define parameters for the query
        # params = attr_name

        cursor.execute(query)

        # Fetch and return the results
        results = cursor.fetchall()
        
        json_results = []
        for row in results:
            # json_result = process_data(row)
            json_results.append(row)
        return json_results

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

data=fetch_data('AutoSenseAnalytics_MPU_Measurement_acc', 'attrValue')
import matplotlib.pyplot as plt

# Extract time and values from the data
times = [datetime.strptime(record[0], '%Y-%m-%d %H:%M:%S.%f') for record in data]
values = [float(record[1]) for record in data]

# Plot the data
plt.figure(figsize=(10, 5))
plt.plot(times, values, marker='o')
plt.xlabel('Time')
plt.ylabel('Value')
plt.title('Value over Time')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
print(data)

# Perform FFT
N = len(values)
T = (times[1] - times[0]).total_seconds()  # Sample spacing
yf = fft(values)
xf = fftfreq(N, T)[:N//2]

# Plot the FFT results
plt.figure(figsize=(10, 5))
plt.plot(xf, 2.0/N * np.abs(yf[:N//2]))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.title('FFT of the Data')
plt.grid(True)
plt.show()

# Define a low-pass filter
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# Apply low-pass filter to the data
cutoff_frequency = 0.1  # Adjust as needed
filtered_values = lowpass_filter(values, cutoff_frequency, 1/T)

# Plot the filtered data
plt.figure(figsize=(10, 5))
plt.plot(times, filtered_values, marker='o')
plt.xlabel('Time')
plt.ylabel('Filtered Value')
plt.title('Filtered Value over Time')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()