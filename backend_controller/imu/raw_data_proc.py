from datetime import datetime
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import butter, filtfilt

import mysql.connector
import ast

db_config = {
    'host': '150.140.186.118',
    'port': 3306,
    'user': 'readonly_student',
    'password': 'iot_password',
    'database': 'default'
}

def calculate_avg_per_sample(x,y,z):
    all_avg_x = []
    all_avg_y = []
    all_avg_z = []
    counter = 0
    print(z[520])
    for i in x:
        if not len(i) == 0:
            avg_x = sum(i)/len(i)
            all_avg_x.append(avg_x)
            counter += 1
    for i in y:
        if not len(i) == 0:
            avg_y = sum(i)/len(i)
            all_avg_y.append(avg_y)
    for i in z:
        if not len(i) == 0:
            avg_z = sum(i)/len(i)
            all_avg_z.append(avg_z)
    
    print(len(all_avg_x))
    print(len(all_avg_y))
    print(len(all_avg_z))
    return all_avg_x, all_avg_y, all_avg_z


def fetch_data(table_name, attr_name, start_datetime=None, end_datetime=None):
    
    try:
        # Establish the connection to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = f"""
            SELECT 
                R1.attrValue AS timestamp,
                R2.attrValue AS location, 
                R4.attrValue AS acc_x, 
                R5.attrValue AS acc_y, 
                R6.attrValue AS acc_z,
                R7.attrValue AS speed,
                R8.attrValue AS altitude
            FROM 
                `default`.AutoSenseAnalytics_IMU_Measurement_raw AS R1 
            JOIN 
                `default`.AutoSenseAnalytics_IMU_Measurement_raw AS R2 
            JOIN 
                `default`.AutoSenseAnalytics_IMU_Measurement_raw AS R4 
            JOIN 
                `default`.AutoSenseAnalytics_IMU_Measurement_raw AS R5  
            JOIN 
                `default`.AutoSenseAnalytics_IMU_Measurement_raw AS R6
            JOIN 
                `default`.AutoSenseAnalytics_IMU_Measurement_raw AS R7
            JOIN 
                `default`.AutoSenseAnalytics_IMU_Measurement_raw AS R8
            ON 
                R1.recvTimeTs = R2.recvTimeTs AND
                R1.recvTimeTs = R4.recvTimeTs AND
                R1.recvTimeTs = R5.recvTimeTs AND
                R1.recvTimeTs = R6.recvTimeTs AND
                R1.recvTimeTs = R7.recvTimeTs AND
                R1.recvTimeTs = R8.recvTimeTs AND
                R2.recvTimeTs = R4.recvTimeTs AND
                R2.recvTimeTs = R5.recvTimeTs AND
                R2.recvTimeTs = R6.recvTimeTs AND
                R2.recvTimeTs = R7.recvTimeTs AND
                R2.recvTimeTs = R8.recvTimeTs AND
                R4.recvTimeTs = R5.recvTimeTs AND
                R4.recvTimeTs = R6.recvTimeTs AND
                R4.recvTimeTs = R7.recvTimeTs AND
                R4.recvTimeTs = R8.recvTimeTs AND
                R5.recvTimeTs = R6.recvTimeTs AND
                R5.recvTimeTs = R7.recvTimeTs AND
                R5.recvTimeTs = R8.recvTimeTs AND
                R6.recvTimeTs = R7.recvTimeTs AND
                R6.recvTimeTs = R8.recvTimeTs
            WHERE 
                R1.attrName = "date" AND 
                R2.attrName = "location" AND
                R4.attrName = "accx" AND 
                R5.attrName = "accy" AND 
                R6.attrName = "accz" AND
                R7.attrName=  "speed" AND
                R8.attrName=  "altitude";
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

data=fetch_data("AutoSenseAnalytics_IMU_Measurement_raw", "timestamp","2025-02-09T15:55:22.000Z","2025-02-09T16:31:02.000Z")
# print(data[-1])
x=[]
y=[]
z=[]
alldata=[]
for row in data:
    parsed_data = [
        ast.literal_eval(item) if isinstance(item, str) and item.startswith('[') and item.endswith(']') else item
        for item in row
     ]
    alldata.append(parsed_data)

    # print(alldata)

#list with all the data
for i in alldata:
    x.append(i[2]) #add the list of the x data of each FIWARE entry
    y.append(i[3]) #add the list list of the y data of each FIWARE entry
    z.append(i[4]) #add the list of the z data of each FIWARE entry

calculate_avg_per_sample(x,y,z)


    



def plot_all_data(x,y,z):
    # Flatten the list of lists for x, y, and z
    x = [item for sublist in x for item in sublist]
    y = [item for sublist in y for item in sublist]
    z = [item for sublist in z for item in sublist]
    import matplotlib.pyplot as plt

    # Plotting the IMU data
    plt.figure(figsize=(12, 6))

    # Plot x-axis data
    plt.subplot(3, 1, 1)
    plt.plot(x, label='Acc X')
    plt.title('IMU Accelerometer Data')
    plt.ylabel('Acc X')
    plt.legend()

    # Plot y-axis data
    plt.subplot(3, 1, 2)
    plt.plot(y, label='Acc Y')
    plt.ylabel('Acc Y')
    plt.legend()

    # Plot z-axis data
    plt.subplot(3, 1, 3)
    plt.plot(z, label='Acc Z')
    plt.xlabel('Sample')
    plt.ylabel('Acc Z')
    plt.legend()


    plt.legend()
    plt.tight_layout()
    plt.show()
# print(y)
# print(z)


# import matplotlib.pyplot as plt

# # Plotting the IMU data
# plt.figure(figsize=(12, 6))

# # Plot x-axis data
# plt.subplot(4, 1, 1)
# plt.plot(x, label='Acc X')
# plt.title('IMU Accelerometer Data')
# plt.ylabel('Acc X')
# plt.legend()

# # Plot y-axis data
# plt.subplot(4, 1, 2)
# plt.plot(y, label='Acc Y')
# plt.ylabel('Acc Y')
# plt.legend()

# # Plot z-axis data
# plt.subplot(4, 1, 3)
# plt.plot(z, label='Acc Z')
# plt.xlabel('Sample')
# plt.ylabel('Acc Z')
# plt.legend()

# # Calculate the magnitude of acceleration to estimate road roughness
# magnitude = np.sqrt(np.array(x)**2 + np.array(y)**2 + np.array(z)**2)

# # Plot the magnitude of acceleration
# plt.subplot(4, 1, 4)
# plt.plot(magnitude, label='Magnitude of Acceleration')
# plt.title('Road Roughness Estimation')
# plt.xlabel('Sample')
# plt.ylabel('Magnitude of Acceleration')
# plt.legend()
# plt.tight_layout()
# plt.show()

# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.signal import butter, filtfilt, welch
# import random
# x.extend(random.sample(range(100), 4))
# y.extend(random.sample(range(100), 4))
# z.extend(random.sample(range(100), 4))
# print(len(x))
# # Bandpass filter implementation
# def butter_bandpass(lowcut, highcut, fs, order=4):
#     nyquist = 0.5 * fs
#     low = lowcut / nyquist
#     high = highcut / nyquist
#     b, a = butter(order, [low, high], btype='band')
#     return b, a

# def bandpass_filter(data, lowcut, highcut, fs, order=4):
#     b, a = butter_bandpass(lowcut, highcut, fs, order=order)
#     y = filtfilt(b, a, data)
#     return y

# # Step 1: Calculate the magnitude of acceleration
# magnitude = np.sqrt(np.array(x)**2 + np.array(y)**2 + np.array(z)**2)

# # Plot raw magnitude
# plt.figure(figsize=(12, 8))
# plt.subplot(4, 1, 1)
# plt.plot(magnitude, label='Raw Magnitude')
# plt.title('Raw Magnitude of Acceleration')
# plt.xlabel('Sample')
# plt.ylabel('Acceleration Magnitude')
# plt.legend()

# # Importing 4 random values to x, y, z


# # Step 2: Apply a bandpass filter
# fs = 50  # Sampling frequency in Hz (adjust based on your data)
# lowcut = 0.1  # Lower frequency bound in Hz
# highcut = 20  # Upper frequency bound in Hz
# filtered_magnitude = bandpass_filter(magnitude, lowcut, highcut, fs)

# # Plot filtered signal
# plt.subplot(4, 1, 2)
# plt.plot(filtered_magnitude, label='Filtered Magnitude', color='orange')
# plt.title('Filtered Magnitude (Bandpass: 0.1-20 Hz)')
# plt.xlabel('Sample')
# plt.ylabel('Filtered Acceleration')
# plt.legend()

# # Step 3: Calculate the RMS of the filtered signal
# rms = np.sqrt(np.mean(filtered_magnitude**2))

# # Highlight RMS value on the plot
# plt.subplot(4, 1, 3)
# plt.plot(filtered_magnitude, label='Filtered Magnitude', color='orange')
# plt.axhline(rms, color='red', linestyle='--', label=f'RMS = {rms:.4f}')
# plt.title('Root Mean Square (RMS) of Filtered Signal')
# plt.xlabel('Sample')
# plt.ylabel('RMS')
# plt.legend()

# # Step 4: Compute and plot the Power Spectral Density (PSD)
# frequencies, psd = welch(filtered_magnitude, fs, nperseg=256)

# plt.subplot(4, 1, 4)
# plt.semilogy(frequencies, psd, label='Power Spectral Density')
# plt.title('Power Spectral Density (PSD)')
# plt.xlabel('Frequency (Hz)')
# plt.ylabel('PSD (Power/Hz)')
# plt.legend()

# plt.tight_layout()
# plt.show()

# # Step 5: Threshold Analysis
# # Define thresholds based on RMS or PSD analysis (example thresholds below):
# if rms < 0.5:
#     road_condition = "Smooth Road"
# elif 0.5 <= rms < 1.0:
#     road_condition = "Moderate Roughness"
# else:
#     road_condition = "Rough Road"

# print(f"RMS: {rms:.4f}, Road Condition: {road_condition}")





