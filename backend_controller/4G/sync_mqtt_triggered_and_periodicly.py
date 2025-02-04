import random
import mysql.connector
import json
import requests
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import pytz
from datetime import datetime
import paho.mqtt.client as mqtt_client
import time
import threading
# Database connection details
db_config = {
    'host': '150.140.186.118',
    'port': 3306,
    'user': 'readonly_student',
    'password': 'iot_password',
    'database': 'default'
}

#FIWARE ORION CB Connection details
fiware_url = "http://150.140.186.118:1026/v2/entities/4G_Measurement/attrs"  

fiware_headers = {
    "Accept": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics"       
}

# InfluxDB connection details
influxdb_url = "http://150.140.186.118:8086"
bucket = "AutoSenseAnalytics4G"
org = "students"
token = "fRML93YyZozXXQI-torGL3PbHXSq04sAbweQTtb4ZKfWGushczd_jnjvxzhgNBHvBIUEQkmHQDicg4tjoTWDhg=="

#mqtt connection details
mqtt_host = '150.140.186.118'
mqtt_topic='autosense/4g_rssi'

#function to fetch data from MySQL Fiware DB, based on the time parameters 
def fetch_data(table_name, attr_name, start_datetime=None, end_datetime=None):
    
    try:
        # Establish the connection to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = f"""
            SELECT R1.recvTimeTs, R1.recvTime, R1.attrName, R1.attrValue, 
               R2.attrName, R2.attrValue, R3.attrName, R3.attrValue, 
               R4.attrName, R4.attrValue,R5.attrName, R5.attrValue
            FROM {table_name} as R1 
            JOIN {table_name} as R2 
            JOIN {table_name} as R3 
            JOIN {table_name} as R4
            JOIN {table_name} as R5
            WHERE R1.attrName = %s 
              AND R2.attrName = %s
              AND R3.attrName = %s
              AND R4.attrName = %s
              AND R5.attrName = %s
              AND R1.recvTimeTs = R2.recvTimeTs 
              AND R1.recvTimeTs = R3.recvTimeTs 
              AND R1.recvTimeTs = R4.recvTimeTs
              AND R1.recvTimeTs = R5.recvTimeTs   
              AND R2.recvTimeTs = R3.recvTimeTs 
              AND R2.recvTimeTs = R4.recvTimeTs
              AND R2.recvTimeTs = R5.recvTimeTs   
              AND R3.recvTimeTs = R4.recvTimeTs
              AND R3.recvTimeTs = R5.recvTimeTs
              AND R4.recvTimeTs = R4.recvTimeTs       
              AND R4.attrValue>='{start_datetime}'
              AND R4.attrValue<='{end_datetime}';
        """
        
        # Define parameters for the query
        params = attr_name

        cursor.execute(query, params)

        # Fetch and return the results
        results = cursor.fetchall()
        
        json_results = []
        for row in results:
            json_result = process_data(row)
            json_results.append(json_result)
        return json_results

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def process_data(data):
    try:
        # print("pre - proc data",data)
        return {
            "rssi": float(data[3]),
            "latitude": json.loads(data[5])['coordinates'][1],
            "longitude": json.loads(data[5])['coordinates'][0],
            "speed": data[7],
            "altitude": data[11],
            "timestamp": data[9]
        }
    except (KeyError,ValueError,TypeError) as e:
        print("Error processing data: ", e)
        return None
    
def get_last_influx():
    # influxdb_url = "http://150.140.186.118:8086"
    # bucket = "test2batch"
    # org = "students"
    # token = "U5PdI0KVW2rkwAYou6ti_-aWv_dsITk6ShtiQ2OiwkRJzatC_WQt2kRZuXx-q14AycVY9UhCfV_vUGsev8WgYA=="

    pass

    client = InfluxDBClient(url=influxdb_url,bucket=bucket, token=token, org=org)

    try:
        print(influxdb_url,bucket)
        query=f'from(bucket: "{bucket}")\
                |> range(start: -1y)\
                |> filter(fn: (r) => r["_measurement"] == "4G_rssi")\
                |> filter(fn: (r) => r["_field"] == "rssi")\
                |> last()'
        tables = client.query_api().query(query, org=org)
        if tables:
            for table in tables:
                for record in table.records:
                    # Get the UTC time directly from the record
                    utc_time = record.get_time()
                    # Format the timestamp in ISO format
                    timestamp = utc_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                    # Print the timestamp for debugging purposes
                    print(f"Last field value timestamp (UTC time): {timestamp}")
                    client.close()
                    return timestamp
        client.close()
        client.flush()
        return None
    except Exception as e:
        print(f"Error retrieving last field value: {e}")
        client.close()
    return None

def get_last_fiware():
    response = requests.get(fiware_url, headers=fiware_headers)

    if response.status_code == 200:
        entity = response.json()
        print("Full entity with service and path:")
        print(entity)
        #return the timestamp
        return entity["date"]["value"]
        
    else:
        print(f"Failed to retrieve entity: {response.status_code}")
        print(response.json())


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

def write_to_influx_one_point(data):
    client = InfluxDBClient(url=influxdb_url, token=token)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    point = Point("4G_rssi")\
            .field("rssi", float(data["rssi"]))\
            .field("latitude", float(data["latitude"]))\
            .field("longitude", float(data["longitude"]))\
            .field("speed", float(data["speed"]))\
            .field("altitude", float(data["altitude"]))\
            .time(convert_to_utc(data["timestamp"]))
    

    write_api.write(bucket, org, point)
    print("Data written to InfluxDB")

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

def sync():
    fiware_last=get_last_fiware()
    influx_last=get_last_influx()

    print(f"Last Fiware timestamp: {fiware_last}")
    print(f"Last InfluxDB timestamp: {influx_last}")

    if influx_last is None:
        print("InfluxDB is empty")
        influx_last = "2024-11-20T00:00:00.000Z"

    if influx_last and fiware_last:
        influx_last_dt = datetime.strptime(influx_last, '%Y-%m-%dT%H:%M:%S.%fZ')
        fiware_last_dt = datetime.strptime(fiware_last, '%Y-%m-%dT%H:%M:%S.%fZ')

        if influx_last_dt >= fiware_last_dt:
            print("InfluxDB is up to date")
        else:
            print("InfluxDB need sync")
            data=fetch_data('AutoSenseAnalytics_4G_Measurement_4G',['rssi','location','speed','date','altitude'],influx_last,fiware_last)
            print(len(data))
            print(data[0])
            
            
            points=[]
            for i in data:
                point=point = Point("4G_rssi")\
                            .field("rssi", float(i["rssi"]))\
                            .field("latitude", float(i["latitude"]))\
                            .field("longitude", float(i["longitude"]))\
                            .field("speed", float(i["speed"]))\
                            .field("altitude", float(i["altitude"]))\
                            .time(i["timestamp"])
                points.append(point)

            # Write the data to InfluxDB
            update_influxdb(points)

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}\n")

    client = mqtt_client.Client('client_id'+str(random.random()))
    # client.username_pw_set(username, password)  # Uncomment if username/password is required
    client.on_connect = on_connect
    client.connect(mqtt_host, 1883)
    return client

# Subscribe to the MQTT topic and when the msg is right Call the sync function
def subscribe(client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        sync()
       
            

        

    client.subscribe(mqtt_topic)
    client.on_message = on_message

#run the mqtt reciever in a loop 
def mqtt_reciever():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()  # Keep the client connected and listening for messages

def periodic_sync():
    sync()
    time.sleep(300)
    periodic_sync()

    
# Start the periodic sync in a separate thread
periodic_thread = threading.Thread(target=periodic_sync)
periodic_thread.daemon = True
periodic_thread.start()

mqtt_reciever()

# data=fetch_data('AutoSenseAnalytics_4G_Measurement_4G',['rssi','location','speed','date','altitude'],'2021-06-01T00:00:00Z','2025-02-04T12:22:34.000Z')
# # write_to_influx_one_point(data[0])
# last_influx=get_last_influx()
# last_fiware=get_last_fiware()

# print(last_influx,last_fiware)
# print(data[0])


        
