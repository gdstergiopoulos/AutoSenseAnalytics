import mysql.connector
import json
import requests
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import pytz
from datetime import datetime

# Database connection details
db_config = {
    'host': '150.140.186.118',
    'port': 3306,
    'user': 'readonly_student',
    'password': 'iot_password',
    'database': 'default'
}

fiware_url = "http://150.140.186.118:1026/v2/entities/elenishome/attrs"  
#entity_id = "elenishome"  # Replace with your entity ID
fiware_headers = {
    "Accept": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics/Wifi"       
}

influxdb_url = "http://150.140.186.118:8086"
bucket = "test4batch"
org = "students"
token = "5WxJWTfxkAha1Pk2Yx9MVFUacJhBONLdMbK840pOLq48trsIlwy6qULCH7zzG5uFn4opIFOyrSWsfH8ggAQiew=="


def fetch_data(table_name, attr_name, start_datetime=None, end_datetime=None):
    """
    Fetches recvTime and attrValue from the specified table for rows where attrName matches 
    and recvTime is between start_datetime and end_datetime.

    Parameters:
    - table_name (str): The name of the table to query.
    - attr_name (str): The attribute name to filter on.
    - start_datetime (str or None): The start datetime (inclusive) in "YYYY-MM-DD HH:MM:SS" format. Defaults to None.
    - end_datetime (str or None): The end datetime (inclusive) in "YYYY-MM-DD HH:MM:SS" format. Defaults to None.
    
    Returns:
    - list of tuples: Each tuple contains (recvTime, attrValue) for each matching row.
    """
    try:
        # Establish the connection to the database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Define the base query
        # query = f"""
        #     SELECT recvTime, attrValue
        #     FROM {table_name}
        #     WHERE attrName = %s
        # """
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

        # Add datetime filtering if start and end datetimes are provided
        # if start_datetime:
        #     query += " AND recvTime >= %s"
        #     params.append(start_datetime)
        # if end_datetime:
        #     query += " AND recvTime <= %s"
        #     params.append(end_datetime)

        # Execute the query with the parameters
        cursor.execute(query, params)

        # Fetch and return the results
        results = cursor.fetchall()
        
        # for row in results:
        #     recvTimeTs, recvTime, attrName1, attrValue1, attrName2, attrValue2, attrName3, attrValue3, attrName4, attrValue4 = row
            # print(f"DateTime: {recvTime}, AttrName1: {attrName1}, AttrValue1: {attrValue1}, AttrName2: {attrName2}, AttrValue2: {attrValue2}, AttrName3: {attrName3}, AttrValue3: {attrValue3}, AttrName4: {attrName4}, AttrValue4: {attrValue4}")
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
    





def get_last_influx():
    # influxdb_url = "http://150.140.186.118:8086"
    # bucket = "test2batch"
    # org = "students"
    # token = "U5PdI0KVW2rkwAYou6ti_-aWv_dsITk6ShtiQ2OiwkRJzatC_WQt2kRZuXx-q14AycVY9UhCfV_vUGsev8WgYA=="

    pass

    client = InfluxDBClient(url=influxdb_url,bucket=bucket, token=token, org=org)

    try:
        query=f'from(bucket: "{bucket}")\
                |> range(start: -1y)\
                |> filter(fn: (r) => r["_measurement"] == "rssi_bssid")\
                |> filter(fn: (r) => r["_field"] == "rssi")\
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


def get_last_fiware():
    response = requests.get(fiware_url, headers=fiware_headers)

    if response.status_code == 200:
        entity = response.json()
        print("Full entity with service and path:")
        print(entity)
        #return the timestamp
        return entity["timestamp"]["value"]
        # print("\nNoise attribute value:")
        # print(entity["noise"]["value"])
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









def sync():
    fiware_last=get_last_fiware()
    influx_last=get_last_influx()

    print(f"Last Fiware timestamp: {fiware_last}")
    print(f"Last InfluxDB timestamp: {influx_last}")

    if influx_last is None:
        influx_last = "2024-11-20T00:00:00.000Z"
    #compare the timestamps
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
            #need to update the influxdb
            #get the data from the fiware
            #process the data
            #write the data to influxdb
            points=[]
            for i in data:
                print(i)
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
    

sync()
        
