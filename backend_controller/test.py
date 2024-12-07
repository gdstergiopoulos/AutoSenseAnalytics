# from sync_mqtt_triggered_and_periodicly import get_last_fiware
# get_last_fiware()

# InfluxDB connection details
from influxdb_client import InfluxDBClient
influxdb_url = "http://150.140.186.118:8086"
bucket = "AutoSenseAnalytics"
org = "students"
token = "oOsRHLaYY8_Wp_89wMVENUlChhoGpJ4x9VwjXDQK69Pb3IYTs0Mw9XsfXl5aOWd7MuX82DtAxiChfajweZIWFA=="


def get_measurements():
    # influxdb_url = "http://150.140.186.118:8086"
    # bucket = "test2batch"
    # org = "students"
    # token = "U5PdI0KVW2rkwAYou6ti_-aWv_dsITk6ShtiQ2OiwkRJzatC_WQt2kRZuXx-q14AycVY9UhCfV_vUGsev8WgYA=="

    pass

    client = InfluxDBClient(url=influxdb_url,bucket=bucket, token=token, org=org)

    try:
        # BE CAREFUL YOU NEED TO PUT UTC TIME IN THE QUERY
        print(influxdb_url,bucket)
        with_gps= []
        all=[]
        query=f'from(bucket: "{bucket}")\
                    |> range(start: 2024-12-06T10:19:35Z, stop: 2024-12-06T10:48:57Z)\
                    |> filter(fn: (r) => r._measurement == "rssi_bssid")\
                    |> filter(fn: (r) => r._field == "rssi" or r._field == "mac_address" or r._field == "latitude" or r._field == "longitude")\
                    |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")\
                    |> keep(columns: ["_time", "rssi", "mac_address", "latitude", "longitude"])'
        tables = client.query_api().query(query)
        if tables:
            for table in tables:
                for record in table.records:
                    if record['latitude'] != 0.0 and record['longitude'] != 0.0:
                        print(record)
                        with_gps.append(record)
                    all.append(record)
            
        client.close()
        return with_gps,all
    except Exception as e:
        print(f"Error retrieving last field value: {e}")
        client.close()
    return None

meas_gps,meas=get_measurements()


