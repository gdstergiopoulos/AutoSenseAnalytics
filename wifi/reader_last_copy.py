import mysql.connector
import json
from influxdb_client import InfluxDBClient, Point
#from influxdb_client.client.write_api import ASYNCHRONOUS
import pytz
import requests
import time
from datetime import datetime
# from fiware_to_influxdb import write_to_influxdb
db_config = {
    'host': '150.140.186.118',
    'port': 3306,
    'user': 'readonly_student',
    'password': 'iot_password',
    'database': 'default'
}

influxdb_url = "http://150.140.186.118:8086"
bucket = "AutoSenseAnalytics"
org = "students"
token = "oOsRHLaYY8_Wp_89wMVENUlChhoGpJ4x9VwjXDQK69Pb3IYTs0Mw9XsfXl5aOWd7MuX82DtAxiChfajweZIWFA=="

measurement = "rssi_bssid"

client = InfluxDBClient(url=influxdb_url, token=token, org=org)
write_api = client.write_api()

#fiware connection
# FIWARE Context Broker details
fiware_url = "http://150.140.186.118:1026/v2/entities/elenishome/attrs"  
#entity_id = "elenishome"  # Replace with your entity ID
fiware_headers = {
    "Accept": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics/Wifi"       
}

def get_last_influx_value():
    try:
        query=' from(bucket: "AutoSenseAnalytics")\
                |> range(start: -1d)\
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
                    return timestamp

        return None
    except Exception as e:
        print(f"Error retrieving last field value: {e}")
    return None

                    

def fetch_data(table_name, attr_name, start_datetime=None, end_datetime=None):
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
        # print("Start datetime: ", start_datetime)
        # print("End datetime: ", end_datetime)
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
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        return json_results

    except mysql.connector.Error as err:
        print(f"Error: {err}")

#    finally:
        # Close the cursor and connection
        # if cursor:
        #     cursor.close()
        # if connection:
        #     connection.close()



def get_last_fiware():
    response = requests.get(fiware_url, headers=fiware_headers)

    if response.status_code == 200:
        entity = response.json()
        #print("Full entity with service and path:")
        #print(entity)
        #return the timestamp
        return entity["timestamp"]["value"]
        # print("\nNoise attribute value:")
        # print(entity["noise"]["value"])
    else:
        print(f"Failed to retrieve entity: {response.status_code}")
        print(response.json())






def process_data(data):
    
    try:
        return {
            "rssi": float(data[3]),
            "mac_address": str(data[5]),
            "latitude": json.loads(data[7])["coordinates"][1],
            "longitude": json.loads(data[7])["coordinates"][0],
            "timestamp": data[9]
        }

       

    except (KeyError, ValueError, TypeError) as e:
        print(f"Error processing data: {e}")
        return None
    

def write_batch_to_influxdb(data):
    # Write the processed data to InfluxDB in batches
    try:
        # Create a list to hold the points
        points = []

        # Create a point for each row of data
        for row in data:
            # Create a point in InfluxDB with the processed data
            point = Point("rssi_bssid") \
                .tag("wifi", "wifi_home") \
                .field("mac_address", str(row["mac_address"])) \
                .field("rssi", float(row["rssi"])) \
                .field("latitude", float(row["latitude"])) \
                .field("longitude", float(row["longitude"])) \
                .time(convert_to_utc(row["timestamp"]))

            # Add the point to the list
            points.append(point)

        # Write the data to InfluxDB
        write_api.write(bucket=bucket, org=org, record=points)
        print(f"Data written to InfluxDB")
        points.clear()
        write_api.close()
        

    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")


# def write_to_influxdb(processed_data):
#     #Write the processed data to InfluxDB
#     try:
#         # Create a point in InfluxDB with the processed data
#         point = Point("rssi_bssid") \
#             .tag("wifi", "wifi_home") \
#             .field("mac_address", processed_data["mac_address"]) \
#             .field("rssi", processed_data["rssi"]) \
#             .field("latitude", processed_data["latitude"]) \
#             .field("longitude", processed_data["longitude"]) \
#             .time(convert_to_utc(processed_data["timestamp"]))

#         # Write the data to InfluxDB
#         write_api.write(bucket=bucket, org=org, record=point)
#         print(f"Data written to InfluxDB: {processed_data}")
    
#     except Exception as e:
#         print(f"Error writing to InfluxDB: {e}")

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
            print(utc_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
            return utc_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        except Exception as e:
            print(f"Error converting timestamp to UTC: {e}")
            return None    

# Example usage
# Fetch and process data from MySQL to influxDB wanted format
# data=fetch_data(
#     table_name="AutoSenseAnalytics_Wifi_elenishome_rssi_bssid",
#     attr_name=['rssi', 'macAddress', 'location', 'timestamp'],
#     start_datetime="2024-10-15 00:00:00",
#     end_datetime="2024-11-17 23:59:59"
# )
# print(data)



# for row in data:
#    # write_to_influxdb(row)
#     print(f"Data written to InfluxDB: {row}")
influx_last=get_last_influx_value()
fiware_last=get_last_fiware()
print("Influx last: ", influx_last)
print("Fiware last: ", fiware_last)
if influx_last and fiware_last:
    influx_last_dt = datetime.strptime(influx_last, '%Y-%m-%dT%H:%M:%S.%fZ')
    fiware_last_dt = datetime.strptime(fiware_last, '%Y-%m-%dT%H:%M:%S.%fZ')

    if influx_last_dt >= fiware_last_dt:
        print("InfluxDB is up to date")
    else:
        data=fetch_data(
            table_name="AutoSenseAnalytics_Wifi_elenishome_rssi_bssid",
            attr_name=['rssi', 'macAddress', 'location', 'timestamp'],
            start_datetime=influx_last,
            end_datetime=fiware_last
        )
        print(f"Fetched {len(data)} rows of data")
        write_batch_to_influxdb(data)
        write_api.close()

else:
    print("Could not retrieve timestamps from both sources.")
# Close the write API

