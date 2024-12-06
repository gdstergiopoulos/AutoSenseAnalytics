import time
import requests
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime
import pytz

#ενδεχομενως προβλημα με το json format και το location 



# InfluxDB connection details
influxdb_url = "http://150.140.186.118:8086"
bucket = "AutoSenseAnalytics"
org = "students"
token = "oOsRHLaYY8_Wp_89wMVENUlChhoGpJ4x9VwjXDQK69Pb3IYTs0Mw9XsfXl5aOWd7MuX82DtAxiChfajweZIWFA=="


# FIWARE Context Broker details
fiware_url = "http://150.140.186.118:1026/v2/entities/elenishome"  
#entity_id = "elenishome"  # Replace with your entity ID
fiware_headers = {
    "Accept": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics/Wifi"       
    
}

# Initialize InfluxDB client
client = InfluxDBClient(url=influxdb_url, token=token, org=org)
write_api = client.write_api()

def fetch_data_from_fiware():
    #Fetch sensor data from FIWARE Context Broker
    try:
        response = requests.get(fiware_url, headers=fiware_headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from FIWARE: {e}")
        return None

def process_data(data):
    try:
        # Ensure rssi is always a float
        rssi = float(data["rssi"]["value"])

        # Ensure mac_address is a string
        mac_address = str(data["macAddress"]["value"])

        # Extract latitude and longitude (or set them to None if missing)
        if (
            "location" in data
            and "value" in data["location"]
            and "coordinates" in data["location"]["value"]
        ):
            location = data["location"]["value"]["coordinates"]
            longitude = float(location[0]) if len(location) > 0 else None
            latitude = float(location[1]) if len(location) > 1 else None
        else:
            latitude, longitude = None, None

        # Ensure timestamp is properly formatted
        timestamp = data["timestamp"]["value"]

        return {
            "rssi": rssi,
            "mac_address": mac_address,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp,
        }

    except (KeyError, ValueError, TypeError) as e:
        print(f"Error processing data: {e}")
        return None
    
def convert_to_utc(timestamp):
        try:
            # Define the Athens timezone
            athens_tz = pytz.timezone('Europe/Athens')
            
            # Parse the timestamp string into a datetime object
            local_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            
            # Localize the datetime object to Athens timezone
            local_time = athens_tz.localize(local_time)
            
            # Convert the localized time to UTC
            utc_time = local_time.astimezone(pytz.utc)
            
            # Return the UTC time in the same format
            return utc_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        except Exception as e:
            print(f"Error converting timestamp to UTC: {e}")
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
            .time(convert_to_utc(processed_data["timestamp"]))

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