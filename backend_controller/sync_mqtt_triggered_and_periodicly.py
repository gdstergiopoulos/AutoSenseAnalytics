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
fiware_url = "http://150.140.186.118:1026/v2/entities/elenishome/attrs"  

fiware_headers = {
    "Accept": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics/Wifi"       
}

# InfluxDB connection details
influxdb_url = "http://150.140.186.118:8086"
bucket = "AutoSenseAnalytics"
org = "students"
token = "oOsRHLaYY8_Wp_89wMVENUlChhoGpJ4x9VwjXDQK69Pb3IYTs0Mw9XsfXl5aOWd7MuX82DtAxiChfajweZIWFA=="

#mqtt connection details
mqtt_host = '150.140.186.118'
mqtt_topic='autosense/wifi'

#function to fetch data from MySQL Fiware DB, based on the time parameters 
def fetch_data(table_name, attr_name, start_datetime=None, end_datetime=None):
    
    try:
        # Establish the connection to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query = f"""
            SELECT R1.recvTimeTs, R1.recvTime, R1.attrName, R1.attrValue, 
               R2.attrName, R2.attrValue, R3.attrName, R3.attrValue, 
               R4.attrName, R4.attrValue
            FROM {table_name} as R1 
            JOIN {table_name} as R2 
            JOIN {table_name} as R3 
            JOIN {table_name} as R4
            WHERE R1.attrName = %s 
              AND R2.attrName = %s
              AND R3.attrName = %s
              AND R4.attrName = %s
              AND R1.recvTimeTs = R2.recvTimeTs 
              AND R1.recvTimeTs = R3.recvTimeTs 
              AND R1.recvTimeTs = R4.recvTimeTs 
              AND R2.recvTimeTs = R3.recvTimeTs 
              AND R2.recvTimeTs = R4.recvTimeTs 
              AND R3.recvTimeTs = R4.recvTimeTs
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

#function to process the data taken from the MySQL Fiware DB
def process_data(data):
    
    try:
        return {
            # "id": int(data[0]),
            "rssi": float(data[3]),
            "mac_address": str(data[5]),
            "latitude": json.loads(data[7])["coordinates"][1],
            "longitude": json.loads(data[7])["coordinates"][0],
            "timestamp": data[9]
        }

       

    except (KeyError, ValueError, TypeError) as e:
        print(f"Error processing data: {e}")
        return None

#function to get the last timestamp from the influxdb data
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
                |> filter(fn: (r) => r["_measurement"] == "rssi_bssid")\
                |> filter(fn: (r) => r["_field"] == "rssi")\
                |> filter(fn: (r) => r["wifi"]=="wifi_home")\
                |> last()'
        tables = client.query_api().query(query, org=org)
        if tables:
            for table in tables:
                for record in table.records:
                     # Convert UTC time to Athens time
                    utc_time = record.get_time()
                    athens_tz = pytz.timezone('Europe/Athens')
                    local_time = utc_time.astimezone(athens_tz)
                    #print(local_time)
                    timestamp = local_time.strftime('%Y-%m-%d %H:%M:%S')
                    #timestamp in iso format
                    timestamp = local_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
                    #print(f"Last field value timestamp (Athens time): {timestamp}")
                    client.close()
                    return timestamp
        client.close()
        client.flush()
        return None
    except Exception as e:
        print(f"Error retrieving last field value: {e}")
        client.close()
    return None

#function to get the last timestamp from the fiware data 
def get_last_fiware():
    response = requests.get(fiware_url, headers=fiware_headers)

    if response.status_code == 200:
        entity = response.json()
        print("Full entity with service and path:")
        print(entity)
        #return the timestamp
        return entity["timestamp"]["value"]
        
    else:
        print(f"Failed to retrieve entity: {response.status_code}")
        print(response.json())

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

#function to write the fiware data to influx
def update_influxdb(points):
    # influxdb_url = "http://150.140.186.118:8086"
    # bucket = "test2batch"
    # org = "students"
    # token = "U5PdI0KVW2rkwAYou6ti_-aWv_dsITk6ShtiQ2OiwkRJzatC_WQt2kRZuXx-q14AycVY9UhCfV_vUGsev8WgYA=="

    client = InfluxDBClient(url=influxdb_url,bucket=bucket, token=token, org=org)
    try:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=bucket, org=org, record=points)
        write_api.flush()
    finally:
        client.close()
        print("InfluxDB updated successfully")

    return 0

#function to sync the data from fiware to influxdb (if needed)
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
            data=fetch_data(
                table_name="AutoSenseAnalytics_Wifi_elenishome_rssi_bssid",
                attr_name=['rssi', 'macAddress', 'location', 'timestamp'],
                start_datetime=influx_last,
                end_datetime=fiware_last
                )
            print(len(data))
            
            
            points=[]
            for i in data:
                point=Point("rssi_bssid")\
                    .tag("wifi", "wifi_home")\
                    .field("mac_address", str(i["mac_address"]))\
                    .field("rssi", float(i["rssi"]))\
                    .field("latitude", float(i["latitude"]))\
                    .field("longitude", float(i["longitude"]))\
                    .time(convert_to_utc(i["timestamp"]))
                points.append(point)

            # Write the data to InfluxDB
            update_influxdb(points)
    
#establish mqtt connection
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
        if (msg.payload.decode() == "Server is awake"):
            print("Server is awake!")
            sync()
        else:
            print("mqtt message not recognized")
            

        

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




        
