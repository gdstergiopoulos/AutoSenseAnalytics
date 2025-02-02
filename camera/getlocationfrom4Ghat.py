import serial
import time

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

                latitude = fields[0] + " " + fields[1]
                longitude = fields[2] + " " + fields[3]
                # date = fields[4]  # DDMMYYYY
                # time_utc = fields[5]  # HHMMSS
                # altitude = fields[6]
                # speed = fields[7]

                return f"Latitude: {latitude}, Longitude: {longitude}"#, Date: {date}, Time: {time_utc} UTC, Altitude: {altitude}, Speed: {speed}"

            return "No GPS data received"
    except Exception as e:
        return f"Error retrieving GPS data: {e}"


serial_port = "/dev/ttyUSB2"  
baud_rate = 115200

gps_location = get_gps_location(serial_port, baud_rate)
print(gps_location)