import time
import requests
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime
import pytz



def sync_indluxdb(car_id):
    # FIWARE Context Broker details
    fiware_url = "http://150.140.186.118:1026/v2/entities/car"+str(car_id)+"/attrs"  

    fiware_headers = {
        "Accept": "application/json",
        "Fiware-ServicePath": "/AutoSenseAnalytics/demo"       
    }

    

    data=fetch_data_from_fiware(fiware_url,fiware_headers)
    processed_data=process_data(data,car_id)
    if processed_data:
        print(processed_data)
        write_to_influxdb(processed_data)    

def fetch_data_from_fiware(fiware_url,fiware_headers):
        #Fetch sensor data from FIWARE Context Broker
        try:
            response = requests.get(fiware_url, headers=fiware_headers)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from FIWARE: {e}")
            return None

def process_data(data,car_id):
    try:
        battery = float(data["battery"]["value"])
        speed = float(data["speed"]["value"])
        rssi_cellular = float(data["rssi_cellular"]["value"])
        rssi_wifi = float(data["rssi_wifi"]["value"])
        rssi_lora = float(data["rssi_lora"]["value"])
        imu_roughness = float(data["imu_roughness"]["value"])
        camera = str(data["camera"]["value"])

        #Extract latitude and longitude (or set them to None if missing)
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
        timestamp = convert_to_utc(timestamp)
        return {
             "car_id": car_id,
            "battery": battery,
            "speed": speed,
            "rssi_cellular": rssi_cellular,
            "rssi_wifi": rssi_wifi,
            "rssi_lora": rssi_lora,
            "imu_roughness": imu_roughness,
            "camera": camera,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp,
        }
    except (KeyError, ValueError, TypeError) as e:
        print(f"Error processing data: {e}")
        return None


     
        
# def process_data(data):
#     try:
#         # Ensure rssi is always a float
#         rssi = float(data["rssi"]["value"])

#         # Ensure mac_address is a string
#         mac_address = str(data["macAddress"]["value"])

#         # Extract latitude and longitude (or set them to None if missing)
#         if (
#             "location" in data
#             and "value" in data["location"]
#             and "coordinates" in data["location"]["value"]
#         ):
#             location = data["location"]["value"]["coordinates"]
#             longitude = float(location[0]) if len(location) > 0 else None
#             latitude = float(location[1]) if len(location) > 1 else None
#         else:
#             latitude, longitude = None, None

#         # Ensure timestamp is properly formatted
#         timestamp = data["timestamp"]["value"]

#         return {
#             "rssi": rssi,
#             "mac_address": mac_address,
#             "latitude": latitude,
#             "longitude": longitude,
#             "timestamp": timestamp,
#         }

#     except (KeyError, ValueError, TypeError) as e:
#         print(f"Error processing data: {e}")
#         return None
    
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
    # InfluxDB connection details
    influxdb_url = "http://150.140.186.118:8086"
    bucket = "AutoSenseAnalytics_demo"
    org = "students"
    token = "2k6fDobnAtVwHJLF4kbkROlZIiNCb3V5_WL2Bnr2vhHVtH8hgTs0htjdOivP19nK7e8ECljmcpDmjRR2BPqlwA=="

    # Initialize InfluxDB client
    client = InfluxDBClient(url=influxdb_url, token=token, org=org)
    write_api = client.write_api()

    #Write the processed data to InfluxDB
    try:
        # Create a point in InfluxDB with the processed data
        point = Point("car_metrics") \
            .tag("car_id", processed_data["car_id"]) \
            .field("battery", processed_data["battery"]) \
            .field("speed", processed_data["speed"]) \
            .field("rssi_cellular", processed_data["rssi_cellular"]) \
            .field("rssi_wifi", processed_data["rssi_wifi"]) \
            .field("rssi_lora", processed_data["rssi_lora"]) \
            .field("imu_roughness", processed_data["imu_roughness"]) \
            .field("camera", processed_data["camera"]) \
            .field("latitude", processed_data["latitude"]) \
            .field("longitude", processed_data["longitude"]) \
            .time(processed_data["timestamp"])

        # Write the data to InfluxDB
        write_api.write(bucket=bucket, org=org, record=point)
        print(f"Data written to InfluxDB: {processed_data}")
    
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")
    finally:
        write_api.close()
        client.close()
