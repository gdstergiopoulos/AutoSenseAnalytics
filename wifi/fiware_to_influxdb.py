import time
import requests
from influxdb_client import InfluxDBClient, Point, WritePrecision

#ενδεχομενως προβλημα με το json format και το location 



# InfluxDB connection details
influxdb_url = "http://150.140.186.118:8086"
bucket = "AutoSenseAnalytics"
org = "students"
token = "oOsRHLaYY8_Wp_89wMVENUlChhoGpJ4x9VwjXDQK69Pb3IYTs0Mw9XsfXl5aOWd7MuX82DtAxiChfajweZIWFA=="
measurement = "elenishome_wifi"

# FIWARE Context Broker details
fiware_url = "http://150.140.186.118:1026/v2/entities"  
entity_id = "elenishome"  # Replace with your entity ID
fiware_headers = {
    #"Fiware-Service": "<fiware_service>",  # Replace with your FIWARE service
    "Fiware-ServicePath": "/AutoSenseAnalytics/Wifi",             
    "Content-Type": "application/json"
}

# Initialize InfluxDB client
client = InfluxDBClient(url=influxdb_url, token=token, org=org)
write_api = client.write_api()

def fetch_data_from_fiware():
    #Fetch sensor data from FIWARE Context Broker
    try:
        response = requests.get(f"{fiware_url}/{entity_id}", headers=fiware_headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from FIWARE: {e}")
        return None

def process_data(data):
    #Extract and process relevant data from the FIWARE response for RSSI, MAC address, location, and timestamp
    try:
        # Extract the RSSI value (signal strength)
        rssi = data["rssi"]["value"]  # The actual signal strength value

        # Extract the MAC address
        mac_address = data["macAddress"]["value"]  # The MAC address value

        # Extract the location (coordinates)
        location = data["location"]["value"]["coordinates"]  # Coordinates from the location data
        latitude = location[1]  # The first value in the list is latitude
        longitude = location[0]  # The second value is longitude

        # Extract the timestamp
        timestamp = data["timestamp"]["value"]  # The timestamp as an ISO format string

        # Return a dictionary with processed data
        return {
            "rssi": float(rssi),
            "mac_address": mac_address,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp
        }
    
    except KeyError as e:
        print(f"Error processing data: Missing key {e}")
        return None
    

def write_to_influxdb(processed_data):
    #Write the processed data to InfluxDB
    try:
        # Create a point in InfluxDB with the processed data
        point = Point("rssi_bssid") \
            .tag("wifi", "wifi_home") \
            .field("mac_address", processed_data["mac_address"]) \
            .field("rssi", processed_data["rssi"]) \
            .field("latitude", processed_data["latitude"]) \
            .field("longitude", processed_data["longitude"]) \
            .time(processed_data["timestamp"], WritePrecision.NS)

        # Write the data to InfluxDB
        write_api.write(bucket=bucket, org=org, record=point)
        print(f"Data written to InfluxDB: {processed_data}")
    
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")

def main():
    while True:
        # Fetch data from FIWARE
        raw_data = fetch_data_from_fiware()
        if raw_data:
            # Process the raw data
            processed_data = process_data(raw_data)
            if processed_data:
                # Write to InfluxDB
                write_to_influxdb(processed_data)
        time.sleep(5)  # Adjust the interval as needed

if __name__ == "__main__":
    main()