import mysql.connector
import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS
# Database connection details
db_config = {
    'host': '150.140.186.118',
    'port': 3306,
    'user': 'readonly_student',
    'password': 'iot_password',
    'database': 'default'
}

influxdb_url = "http://150.140.186.118:8086"
bucket = "AutoSenseAnalyticsWifi"
org = "students"
token = "jkI_Bn1t6eUWgXg2Q5xxoS5k9HiKUpgTs_Ru0yetoz5NEjSYS-QA0ahjkhR5fwRO2gjR4KhnocOSlIMSDI-x6Q=="
measurement = "rssi_bssid"

client = InfluxDBClient(url=influxdb_url, token=token, org=org)
write_api = client.write_api()


def get_last_field_value():
    try:
        query=' from(bucket: "AutoSenseAnalyticsWifi")\
                |> range(start: 0)\
                 |> filter(fn: (r) => r["_measurement"] == "rssi_bssid")\
                |> filter(fn: (r) => r["_field"] == "rssi")\
                |> sort(columns: ["_time"], desc: true)\
                |> limit(n: 1)'
        tables = client.query_api().query(query, org=org)
        if tables:
            for table in tables:
                for record in table.records:
                    print(f"Last field value: {record.get_time()}")
                    timestamp = record.get_time().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"Last field value timestamp: {timestamp}")
                    return record.get_value()

        return None
    except Exception as e:
        print(f"Error retrieving last field value: {e}")
    return None




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
              AND R3.recvTimeTs = R4.recvTimeTs;
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
            "id": int(data[0]),
            "rssi": float(data[3]),
            "mac_address": str(data[5]),
            "latitude": json.loads(data[7])["coordinates"][1],
            "longitude": json.loads(data[7])["coordinates"][0],
            "timestamp": data[9]
        }

       

    except (KeyError, ValueError, TypeError) as e:
        print(f"Error processing data: {e}")
        return None
    
def write_to_influxdb(processed_data):
    #Write the processed data to InfluxDB
    try:
        # Create a point in InfluxDB with the processed data
        point = Point("test") \
            .tag("area", "elenhome") \
            .field("id", processed_data["id"]) \
            .field("mac_address", processed_data["mac_address"]) \
            .field("rssi", processed_data["rssi"]) \
            .field("latitude", processed_data["latitude"]) \
            .field("longitude", processed_data["longitude"]) \
            .time(processed_data["timestamp"])
        
        write_api.write(bucket, org, record=point)
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")



# Example usage
# Fetch and process data from MySQL to influxDB wanted format
data=fetch_data(
    table_name="AutoSenseAnalytics_Wifi_elenishome_rssi_bssid",
    attr_name=['rssi', 'macAddress', 'location', 'timestamp'],
    start_datetime="2024-10-15 00:00:00",
    end_datetime="2024-11-17 23:59:59"
)
print(data)



for row in data:
   # write_to_influxdb(row)
    print(f"Data written to InfluxDB: {row}")
get_last_field_value()

# Close the write API
write_api.__del__()
