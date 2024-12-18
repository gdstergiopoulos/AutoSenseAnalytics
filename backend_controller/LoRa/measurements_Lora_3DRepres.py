import requests
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

# Constants
EARTH_RADIUS = 6371000  # in meters

# Convert latitude and longitude to grid coordinates
def lat_lon_to_grid(lat, lon, grid_size):
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    x = EARTH_RADIUS * lon_rad * np.cos(lat_rad)
    y = EARTH_RADIUS * lat_rad
    return int(x // grid_size), int(y // grid_size)

# Get data
def get_data():
    url = 'http://localhost:3000/api/measurements/lora'
    response = requests.get(url)
    return response.json()

data = get_data()
print(data)

# # Filter out measurements with rssi <= -200
# data = [item for item in data if item['rssi'] > -200]

# # Group data by grid coordinates
# grid_size = 5  # in meters
# grid_data = defaultdict(list)
# for item in data:
#     grid_coord = lat_lon_to_grid(item['latitude'], item['longitude'], grid_size)
#     grid_data[grid_coord].append(item['rssi'])

# # Calculate average RSSI for each grid cell
# avg_rssi_data = []
# for grid_coord, rssis in grid_data.items():
#     avg_rssi = sum(rssis) / len(rssis)
#     avg_rssi_data.append({
#         'grid_coord': grid_coord,
#         'avg_rssi': avg_rssi
#     })

# # Extract latitude and longitude from grid coordinates for plotting
# latitudes = [item['grid_coord'][1] * grid_size / EARTH_RADIUS for item in avg_rssi_data]
# longitudes = [item['grid_coord'][0] * grid_size / (EARTH_RADIUS * np.cos(np.radians(lat))) for item, lat in zip(avg_rssi_data, latitudes)]
# avg_rssis = [item['avg_rssi'] for item in avg_rssi_data]

# # Create 2D histogram
# plt.hist2d(longitudes, latitudes, bins=[30, 30], weights=avg_rssis, cmap='Blues')
# plt.colorbar(label='Average RSSI')
# plt.xlabel('Longitude')
# plt.ylabel('Latitude')
# plt.title('2D Histogram of Average RSSI Measurements')
# plt.show()

# Filter out measurements with rssi <= -200
data = [item for item in data if item['rssi'] > -200]

# Extract latitude, longitude, and RSSI for plotting
latitudes = [item['latitude'] for item in data]
longitudes = [item['longitude'] for item in data]
rssis = [item['rssi'] for item in data]

# Create 3D scatter plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
sc = ax.scatter(longitudes, latitudes, rssis, c=rssis, cmap='viridis')

# Add color bar
plt.colorbar(sc, label='RSSI')

# Set labels
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_zlabel('RSSI')
ax.set_title('3D Scatter Plot of RSSI Measurements')

plt.show()



