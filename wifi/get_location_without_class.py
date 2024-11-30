import serial
import time



def fetch_gps_data(serial_port="/dev/ttyS0", baud_rate=9600):
    """
    Initialize the serial connection, fetch GPS data, and return latitude and longitude.

    Parameters:
    - serial_port: The serial port to use (default is "/dev/ttyS0").
    - baud_rate: The baud rate for the serial connection (default is 9600).

    Returns:
    - A tuple of (latitude, longitude). If no GPS signal, returns (0.0, 0.0).
    """
    try:
        # Initialize serial connection
        ser = serial.Serial(serial_port, baud_rate)
        ser.flushInput()  # Clear any existing data in the buffer
        time.sleep(0.5)   # Allow time for the connection to stabilize

        # Read data from the LoRa module
        ser.flushInput()  # Clear buffer before reading fresh data
        time.sleep(0.5)   # Wait briefly for new data to arrive

        if ser.inWaiting() > 0:  # Check if there is data in the buffer
            r_buff = ser.read(ser.inWaiting())  # Read all available data
            message = r_buff.decode("utf-8")   # Decode received bytes into a string
            lines = message.split("\r\n")      # Split into lines

            for line in lines:
                if line.startswith("$GNRMC"):  # Look for GPS sentences
                    parts = line.split(",")
                    if len(parts) > 6:
                        status = parts[2]  # Status field (A=Active, V=Void)
                        if status == "A":  # Valid GPS signal
                            lat = parts[3]
                            lon = parts[5]

                            # Convert latitude and longitude to decimal degrees
                            lat_deg = int(lat[:2])
                            lat_min = float(lat[2:])
                            latitude = lat_deg + (lat_min / 60)
                            if parts[4] == "S":  # South is negative
                                latitude = -latitude

                            lon_deg = int(lon[:3])
                            lon_min = float(lon[3:])
                            longitude = lon_deg + (lon_min / 60)
                            if parts[6] == "W":  # West is negative
                                longitude = -longitude

                            return latitude, longitude
        # If no data or invalid signal, return default
        return 0.0, 0.0
    except Exception as e:
        print(f"Error: {e}")
        return 0.0, 0.0
    finally:
        try:
            ser.close()  # Ensure the serial connection is closed
        except:
            pass

# Example Usage
if __name__ == "__main__":
    while True:
        print("Fetching GPS data...")
        latitude, longitude = fetch_gps_data()
        print(f"Latitude: {latitude:.5f}")
        print(f"Longitude: {longitude:.5f}")
        time.sleep(10)  # Fetch data every 10 seconds


# # Configuration
# SERIAL_PORT = "/dev/ttyS0"
# BAUD_RATE = 9600
# START_FREQ = 850  # Start frequency of LoRa module

# def init_serial():
#     """Initialize the serial connection."""
#     ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
#     ser.flushInput()
#     return ser

# def receive_data(ser):
#     """Receive and process GPS data from the LoRa module."""
#     ser.flushInput()
#     time.sleep(0.5)  # Wait for data to be fully received
#     if ser.inWaiting() > 0:
#         time.sleep(0.5)  # Wait for data to be fully received
#         r_buff = ser.read(ser.inWaiting())

#         # Decode message and process GPS data
#         try:
#             message = r_buff[3:-1].decode("utf-8")  # Extract message content
#             lines = message.split("\r\n")

#             for line in lines:
#                 if line.startswith("$GNRMC"):  # Process only GPS sentences
#                     parts = line.split(",")
#                     if len(parts) > 6:
#                         status = parts[2]  # Status field (A=Active, V=Void)
#                         if status == "A":  # Valid GPS signal
#                             lat = parts[3]
#                             lon = parts[5]

#                             # Convert latitude and longitude to decimal degrees
#                             lat_deg = int(lat[:2])
#                             lat_min = float(lat[2:])
#                             lat_standard = lat_deg + (lat_min / 60)
#                             lat_direction = "N" if parts[4] == "N" else "S"

#                             lon_deg = int(lon[:3])
#                             lon_min = float(lon[3:])
#                             lon_standard = lon_deg + (lon_min / 60)
#                             lon_direction = "E" if parts[6] == "E" else "W"

#                             # Print the GPS coordinates
#                             print(f"Latitude: {lat_standard:.5f} {lat_direction}")
#                             print(f"Longitude: {lon_standard:.5f} {lon_direction}")
#                         else:
#                             # No GPS signal
#                             print("No GPS signal received.")
#                             print("Latitude: 0.00000")
#                             print("Longitude: 0.00000")
#         except Exception as e:
#             print(f"Error decoding GPS data: {e}")

# # Main Logic
# def main():
#     print("Fetching GPS data every 10 seconds...")
#     ser = init_serial()  # Initialize serial connection

#     try:
#         while True:
#             print("\n--- Fetching GPS Data ---")
#             receive_data(ser)  # Receive and process GPS data
#             time.sleep(10)     # Wait for 10 seconds
#     except KeyboardInterrupt:
#         print("\nExiting program...")
#     finally:
#         ser.close()  # Close serial connection

# if __name__ == "__main__":
#     main()