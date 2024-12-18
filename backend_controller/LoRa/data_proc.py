from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import requests
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

#influxdb
org="students"
bucket="testproc"
token="Om7csZjKnfCnYUXFZRYo1BSo7TeXDikSkAAZcWv8hqJqzMKMbFnKc0WqcbaJ69FIk9R-E88JU2OCW8WbacJaTA=="
url="http://150.140.186.118:8086/"

# Get data
def get_data():
    url = 'http://localhost:3000/api/measurements/lora'
    response = requests.get(url)
    return response.json()


# Constants
EARTH_RADIUS = 6371000  # in meters

# Convert latitude and longitude to grid coordinates
def lat_lon_to_grid(lat, lon, grid_size):
    """Convert latitude and longitude to discrete grid coordinates."""
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    x = EARTH_RADIUS * lon_rad * np.cos(lat_rad)
    y = EARTH_RADIUS * lat_rad
    return int(x // grid_size), int(y // grid_size)

# Function to group and average data
def group_and_average_data(data, grid_size):
    """Group nearby points into grid cells and compute average RSSI."""
    grid_data = defaultdict(list)
    
    # Group RSSI by grid coordinates
    for item in data:
        grid_coord = lat_lon_to_grid(item['latitude'], item['longitude'], grid_size)
        grid_data[grid_coord].append(item['rssi'])
    
    # Calculate the average RSSI for each grid cell
    avg_data = []
    avg_data_to_send = []
    for grid_coord, rssis in grid_data.items():
        avg_rssi = sum(rssis) / len(rssis)
        avg_data.append({
            'grid_coord': grid_coord,
            'avg_rssi': avg_rssi
        })
        lat = grid_coord[1] * grid_size / EARTH_RADIUS
        lon = grid_coord[0] * grid_size / (EARTH_RADIUS * np.cos(lat))
        avg_data_to_send.append({
            'latitude': np.degrees(lat),
            'longitude': np.degrees(lon),
            'rssi': avg_rssi
        })

    
    return avg_data,avg_data_to_send

# Extract latitude and longitude from grid coordinates
def grid_to_lat_lon(grid_data, grid_size):
    """Convert grid coordinates back to latitude and longitude."""
    latitudes = []
    longitudes = []
    avg_rssis = []
    
    for item in grid_data:
        grid_coord = item['grid_coord']
        avg_rssi = item['avg_rssi']
        
        x = grid_coord[0] * grid_size
        y = grid_coord[1] * grid_size
        lat = y / EARTH_RADIUS
        lon = x / (EARTH_RADIUS * np.cos(lat))
        
        latitudes.append(np.degrees(lat))
        longitudes.append(np.degrees(lon))
        avg_rssis.append(avg_rssi)
    
    return latitudes, longitudes, avg_rssis

# Main Code
data = get_data()  # Get data from your API

# Filter out measurements with RSSI <= -200
data = [item for item in data if item['rssi'] > -200]

# Set grid size in meters
grid_size = 25  # Adjust this based on your dataset

# Group and average the data
avg_data,avg_data_send = group_and_average_data(data, grid_size)

# Convert grid data back to latitudes and longitudes for plotting
latitudes, longitudes, avg_rssis = grid_to_lat_lon(avg_data, grid_size)

# Create 3D scatter plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
sc = ax.scatter(longitudes, latitudes, avg_rssis, c=avg_rssis, cmap='viridis')

# Add color bar
plt.colorbar(sc, label='Average RSSI')

# Set labels
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_zlabel('RSSI')
ax.set_title('3D Scatter Plot of Averaged RSSI Measurements')

plt.show()

# # Send averaged data to server
# def send_data_to_server(avg_data):
#     url = 'http://localhost:3000/api/measurements/processed'
#     headers = {'Content-Type': 'application/json'}
#     response = requests.post(url, json=avg_data, headers=headers)
#     return response.status_code, response.text

# # Send the averaged data
# status_code, response_text = send_data_to_server(avg_data_send)
# print(f'Status Code: {status_code}')
# print(f'Response: {response_text}')


def update_influxdb(points):

    client = InfluxDBClient(url=url,bucket=bucket, token=token, org=org)
    try:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=bucket, org=org, record=points)
        write_api.flush()
    finally:
        client.close()
        print("InfluxDB updated successfully")

    return 0

# Store the averaged data in InfluxDB
def write_proc_to_data(data):
    
    
    client = InfluxDBClient(url=url,bucket=bucket, token=token, org=org)
    write_api=client.write_api(write_options=SYNCHRONOUS)
    for i in data:
        point = Point("LoraMeasurement_proc") \
                .field("rssi", float(i["rssi"]))\
                .field("latitude", float(i["latitude"]))\
                .field("longitude", float(i["longitude"]))
        print(point)
        write_api.write(bucket=bucket, org=org, record=point)
        write_api.flush()
    client.close()
        


# Write the processed data to InfluxDB
# write_proc_to_data(avg_data_send)