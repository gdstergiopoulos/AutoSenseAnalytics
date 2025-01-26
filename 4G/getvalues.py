import serial
import time

# Serial port configuration
SERIAL_PORT = "/dev/ttyUSB2"  # Replace with your actual port
BAUD_RATE = 115200
TIMEOUT = 1



def send_at_command(serial_conn, command, delay=1):
    """
    Sends an AT command to the modem and reads the response.
    """
    try:
        serial_conn.write(f"{command}\r".encode())
        time.sleep(delay)
        response = serial_conn.read(serial_conn.in_waiting or 1000)
        print(response)
        return [response.decode()]
    except Exception as e:
        print(f"Error sending command {command}: {e}")
        return []

def get_rssi(serial_conn):
    """
    AT+CSQ.
    """
    response = send_at_command(serial_conn, "AT+CSQ")
    try:
        for line in response:
            if "+CSQ:" in line:
                # Extract RSSI and BER from response
                rssi_index = int(line.split(":")[1].split(",")[0].strip())
                # Convert RSSI index to dBm
                if rssi_index == 99:
                    return "Signal not detectable"
                rssi_dbm = -113 + (rssi_index * 2)
                return f"{rssi_dbm} dBm"
    except Exception as e:
        print(f"Error parsing RSSI: {e}")

def get_gps_info(serial_conn):
    """
    AT+CGPSINFO.
    """
    
    send_at_command(serial_conn, "AT+CGPS=1", delay=2)

    response = send_at_command(serial_conn, "AT+CGPSINFO", delay=2)
    try:
        for line in response:
            if "+CGPSINFO:" in line:
                gps_data = line.split(":")[1].strip()
                if gps_data == ",,,,,,,,": 
                    return "No GPS fix available"
                return parse_gps_info(gps_data)
    except Exception as e:
        print(f"Error parsing GPS data: {e}")

        

def parse_gps_info(gps_data):
    try:
        fields = gps_data.split(",")
        if len(fields) < 8:
            return "Incomplete GPS data"

        latitude = fields[0] + " " + fields[1]
        longitude = fields[2] + " " + fields[3]
        date = fields[4]  # DDMMYYYY
        time_utc = fields[5]  # HHMMSS
        altitude = fields[6]
        speed = fields[7]

        return f"Latitude: {latitude}, Longitude: {longitude}, Date: {date}, Time: {time_utc} UTC, Altitude: {altitude}, Speed: {speed}"
    except Exception as e:
        print(f"Error parsing GPS data: {e}")

def main():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
            print("Serial connection established")
            send_at_command(ser, "AT")
            
            time.sleep(1)
            
            rssi = get_rssi(ser)
            print(f"RSSI: {rssi}")

            print("Fetching GPS location...")
            gps_info = get_gps_info(ser)
            print(f"GPS Info: {gps_info}")

            # Stop GPS if needed
            send_at_command(ser, "AT+CGPS=0")
    except Exception as e:
        print(f"Error opening serial port: {e}")

if __name__ == "__main__":
    main()
