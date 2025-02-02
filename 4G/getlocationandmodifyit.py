import serial
import time
import json
import requests
from datetime import datetime



SERIAL_PORT = "/dev/ttyUSB3"  
BAUD_RATE = 115200
TIMEOUT = 1


def create_json(rssi, gps_info):
    measurement = {
        "location": {
            "value": {
                "type": "Point",
                "coordinates": [gps_info.get("latitude"), gps_info.get("longitude")]
            },
            "type": "geo:json"
        },
        "date": {
            "value": gps_info.get("date"),
            "type": "DateTime"
        },
        "altitude": {
            "value": gps_info.get("altitude"),
            "type": "Number"
        },
        "speed": {
            "value": gps_info.get("speed"),
            "type": "Number"
        }
    }
    return measurement



def send_at_command(serial_conn, command, delay=1):
    try:
        serial_conn.write(f"{command}\r".encode())
        time.sleep(delay)
        response = serial_conn.read(serial_conn.in_waiting or 1000)
        print(response) 
        return [response.decode()]
    except Exception as e:
        print(f"Error sending command {command}: {e}")
        return []



def get_gps_info(serial_conn):
    """
    AT+CGPSINFO.
    """

    response = send_at_command(serial_conn, "AT+CGPSINFO", delay=2)
    try:
        for line in response:
            if "+CGPSINFO:" in line:
                gps_data = line.split(":")[1].strip()
                # if gps_data == ",,,,,,,,": 
                #     return "No GPS fix available"
                return parse_gps_info(gps_data)
    except Exception as e:
        print(f"Error parsing GPS data: {e}")



def convert_nmea_to_decimal(nmea_coord, direction):
    """ Convert NMEA format (DDMM.MMMM) to Decimal Degrees (DD.DDDDD) """
    if not nmea_coord or nmea_coord == "":
        return None  # Handle missing data

    degrees = int(float(nmea_coord) / 100)  # Extract degrees
    minutes = float(nmea_coord) % 100 / 60  # Convert minutes to decimal

    decimal_coord = degrees + minutes
    if direction in ["S", "W"]:  # South and West are negative
        decimal_coord *= -1

    return round(decimal_coord, 6)  # Round to 6 decimal places

def format_gps_datetime(date_str, time_str):
    """ Convert GPS date (DDMMYY) and time (HHMMSS) into ISO 8601 format """
    if not date_str or not time_str:
        return "1970-01-01T00:00:00Z"  

    try:
        
        time_str = time_str.split(".")[0]  

        
        if len(date_str) == 6:  # Check if date is in YYMMDD format
            year = "20" + date_str[4:6]  # Convert YY to YYYY
            date_str = date_str[:4] + year  # New format: DDMMYYYY

       
        formatted_datetime = datetime.strptime(date_str + time_str, "%d%m%Y%H%M%S").isoformat() + "Z"
        return formatted_datetime
    except ValueError as e:
        print(f"Error formatting GPS DateTime: {e}")  
        return "1970-01-01T00:00:00Z"  


def parse_gps_info(gps_data):
    try:
        if gps_data == ",,,,,,,,": 
            raise ValueError("No GPS fix available")
        fields = gps_data.split(",")
        if len(fields) < 8:
            raise ValueError("Insufficient GPS data")
        

        print(f"Raw GPS Date: {fields[4]}, Raw GPS Time: {fields[5]}")

        
        latitude = convert_nmea_to_decimal(fields[0], fields[1])
        longitude = convert_nmea_to_decimal(fields[2], fields[3])
        isodatetime = format_gps_datetime(fields[4], fields[5])
        return {
            "latitude": latitude,
            "longitude": longitude,
            "date": isodatetime,
            "altitude": float(fields[6]),
            "speed": float(fields[7]),
        }

    except Exception as e:
         return {
            "latitude": 9999,
            "longitude": 9999,
            "date": "1970-01-01T00:00:00Z",
            "altitude": 0,
            "speed": 0,
            "error": "Error parsing GPS data"
        }

def get_gps_location(serial_port, baud_rate, timeout=1):
    try:
        with serial.Serial(serial_port, baud_rate, timeout) as ser:
            ser.write(b"AT+CGPS=1\r")
            time.sleep(1)
                
            ser.write(b"AT+CGPSINFO\r")
            time.sleep(2)
            response = ser.read(ser.in_waiting or 1000).decode()
            try:
                for line in response:
                    if "+CGPSINFO:" in line:
                        gps_data = line.split(":")[1].strip()
                        return parse_gps_info(gps_data)
            except Exception as e:
                print(f"Error parsing GPS data: {e}")

                gps_info = get_gps_info(ser)
                print(f"GPS Info: {gps_info}")
                
                measurement=create_json(rssi, gps_info)
                print(measurement)
                if measurement:
                    # post_to_fiware(measurement,fiware_url=fiware_url, headers=headers)    
                    patch_measurement(measurement,fiware_url+"/4G_Measurement/attrs", headers)

                
                time.sleep(5)

            # send_at_command(ser, "AT+CGPS=0")
    except Exception as e:
        print(f"Error opening serial port: {e}")

if __name__ == "__main__":
    main()
