import serial
import time


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


def get_gps_location(serial_port, baud_rate, timeout=1):

    try:
        with serial.Serial(serial_port, baud_rate, timeout=timeout) as ser:
            ser.write(b"AT+CGPS=1\r")
            time.sleep(2)  

            ser.write(b"AT+CGPSINFO\r")
            time.sleep(2)

            response = ser.read(ser.in_waiting or 1000).decode()

            if "+CGPSINFO:" in response:
                gps_data = response.split(":")[1].strip()
                if gps_data == ",,,,,,,,": 
                    return "No GPS fix available"

                fields = gps_data.split(",")
                if len(fields) < 8:
                    return "Incomplete GPS data"

                latitude = convert_nmea_to_decimal(fields[0], fields[1])
                longitude = convert_nmea_to_decimal(fields[2], fields[3])
                # date = fields[4]  # DDMMYYYY
                # time_utc = fields[5]  # HHMMSS
                # altitude = fields[6]
                # speed = fields[7]

                return latitude, longitude 
            

            return "No GPS data received"
    except Exception as e:
        return f"Error retrieving GPS data: {e}"


serial_port = "/dev/ttyUSB2"  
baud_rate = 115200

# gps_location = get_gps_location(serial_port, baud_rate)
# print(gps_location)