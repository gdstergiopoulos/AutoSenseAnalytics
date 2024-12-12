import mysql.connector
import json
import requests

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

    

mysql_data=fetch_data(table_name,["rssi","location","timestamp"])
print(mysql_data)