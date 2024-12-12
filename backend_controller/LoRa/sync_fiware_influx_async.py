import mysql.connector
import json
import requests
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import pytz
from datetime import datetime


#Connection Details

#FIWARE MySQL (Cygnus)

db_config = {
    'host': '150.140.186.118',
    'port': 3306,
    'user': 'readonly_student',
    'password': 'iot_password',
    'database': 'default'
}

table_name = "AutoSenseAnalytics_LoRa_LoraMeasurement_rssi"

#InfluxDB Connection Details
influxdb_url = "http://150.140.186.118:8086"
bucket = "AutoSenseAnalytics_LoRa"
org = "students"
token = "gyQjt9HYA8gzzQG1EjpW8GZV7RtbYBulx6UuCLRZUbqCagI9FR5FziuKy4CRIfTS-MY8t_z_-8g70v1ldFuriw=="

#FIWARE ORION CB Connection Details
fiware_url = "http://150.140.186.118:1026/v2/entities/LoraMeasurement/attrs"

fiware_headers = {
    "Accept": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics/LoRa"       
}

#fetch MySQL data
def fetch_data(table_name,attr_name, start_datetime=None,end_datetime=None):
    try:
        # Establish the connection to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = f"""
            SELECT DISTINCT R1.attrName, R1.attrValue, 
               R2.attrName, R2.attrValue, R3.attrName, R3.attrValue 
            FROM {table_name} as R1 
            JOIN {table_name} as R2 
            JOIN {table_name} as R3 
            WHERE R1.attrName = %s 
              AND R2.attrName = %s
              AND R3.attrName = %s
              AND R1.recvTimeTs = R2.recvTimeTs 
              AND R1.recvTimeTs = R3.recvTimeTs 
              AND R2.recvTimeTs = R3.recvTimeTs;
        """
        
        # Define parameters for the query
        params = attr_name

        cursor.execute(query, params)

        # Fetch and return the results
        results = cursor.fetchall()
        
        json_results = []
        counter=0
        for row in results:
            counter=counter+1
            json_result = process_data(row)
            # print(json_result)
            json_results.append(json_result)
        return json_results
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def process_data(data):
    # Create the JSON object
    try:
        return{
            "rssi": float(data[1]),
            "latitude": json.loads(data[3])["coordinates"][1],
            "longitude": json.loads(data[3])["coordinates"][0],
            "timestamp": data[5]
        }
    
    except (KeyError, ValueError, TypeError) as e:
        print(f"Error processing data: {e}")
        return None

#function to convert the timestamp to UTC
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
            #print(utc_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
            return utc_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        except Exception as e:
            print(f"Error converting timestamp to UTC: {e}")
            return None   

def update_influxdb(points):
    client = InfluxDBClient(url=influxdb_url,bucket=bucket, token=token, org=org)
    try:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=bucket, org=org, record=points)
        write_api.flush()
    finally:
        client.close()
        print("InfluxDB updated successfully")

    return 0


mysql_data=fetch_data(table_name,["rssi","location","timestamp"])
points=[]
for i in mysql_data:
    point = Point("LoraMeasurement") \
        .tag("LoRa", "Uni") \
        .field("rssi", float(i["rssi"]))\
        .field("latitude", float(i["latitude"]))\
        .field("longitude", float(i["longitude"]))\
        .time(convert_to_utc(i["timestamp"]))
    points.append(point)

update_influxdb(points)