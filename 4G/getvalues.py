import serial
import time

# Serial port configuration
SERIAL_PORT = "/dev/ttyUSB0"  # Replace with your actual port
BAUD_RATE = 115200
TIMEOUT = 1

def send_at_command(serial_conn, command, delay=1):
    """
    Sends an AT command to the modem and reads the response.
    """
    try:
        serial_conn.write(f"{command}\r".encode())
        time.sleep(delay)
        response = serial_conn.readlines()
        return [line.decode().strip() for line in response]
    except Exception as e:
        print(f"Error sending command {command}: {e}")
        return []

def get_rssi(serial_conn):
    """
    Gets the RSSI (signal strength) using AT+CSQ.
    """
    response = send_at_command(serial_conn, "AT+CSQ")
    for line in response:
        if "+CSQ:" in line:
            # Extract RSSI and BER from response
            rssi_index = int(line.split(":")[1].split(",")[0].strip())
            # Convert RSSI index to dBm
            if rssi_index == 99:
                return "Signal not detectable"
            rssi_dbm = -113 + (rssi_index * 2)
            return f"{rssi_dbm} dBm"
    return "Failed to get RSSI"

def get_gps_info(serial_conn):
    """
    Gets the GPS location using AT+CGPSINFO.
    """
    # Start GPS if not already running
    send_at_command(serial_conn, "AT+CGPS=1", delay=2)

    # Get GPS info
    response = send_at_command(serial_conn, "AT+CGPSINFO", delay=2)
    for line in response:
        if "+CGPSINFO:" in line:
            gps_data = line.split(":")[1].strip()
            if gps_data == ",,,,,,,,":  # No GPS fix yet
                return "No GPS fix available"
            return parse_gps_info(gps_data)
    return "Failed to get GPS info"

def parse_gps_info(gps_data):
    """
    Parses the GPS data returned by AT+CGPSINFO.
    """
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

def main():
    try:
        # Open the serial connection
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
            print("Fetching RSSI...")
            rssi = get_rssi(ser)
            print(f"RSSI: {rssi}")

            print("Fetching GPS location...")
            gps_info = get_gps_info(ser)
            print(f"GPS Info: {gps_info}")

            # Stop GPS if needed
            send_at_command(ser, "AT+CGPS=0")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
