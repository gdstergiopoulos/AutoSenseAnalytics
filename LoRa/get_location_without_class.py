import serial
import time

# Configuration
SERIAL_PORT = "/dev/ttyS0"
BAUD_RATE = 9600
START_FREQ = 850  # Start frequency of LoRa module

def init_serial():
    """Initialize the serial connection."""
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
    ser.flushInput()
    return ser

def receive_data(ser):
    """Receive and process GPS data from the LoRa module."""
    if ser.inWaiting() > 0:
        time.sleep(0.5)  # Wait for data to be fully received
        r_buff = ser.read(ser.inWaiting())

        # Decode message and process GPS data
        try:
            message = r_buff[3:-1].decode("utf-8")  # Extract message content
            lines = message.split("\r\n")

            for line in lines:
                if line.startswith("$GNRMC"):  # Process only GPS sentences
                    parts = line.split(",")
                    if len(parts) > 6:
                        status = parts[2]  # Status field (A=Active, V=Void)
                        if status == "A":  # Valid GPS signal
                            lat = parts[3]
                            lon = parts[5]

                            # Convert latitude and longitude to decimal degrees
                            lat_deg = int(lat[:2])
                            lat_min = float(lat[2:])
                            lat_standard = lat_deg + (lat_min / 60)
                            lat_direction = "N" if parts[4] == "N" else "S"

                            lon_deg = int(lon[:3])
                            lon_min = float(lon[3:])
                            lon_standard = lon_deg + (lon_min / 60)
                            lon_direction = "E" if parts[6] == "E" else "W"

                            # Print the GPS coordinates
                            print(f"Latitude: {lat_standard:.5f} {lat_direction}")
                            print(f"Longitude: {lon_standard:.5f} {lon_direction}")
                        else:
                            # No GPS signal
                            print("No GPS signal received.")
                            print("Latitude: 0.00000")
                            print("Longitude: 0.00000")
        except Exception as e:
            print(f"Error decoding GPS data: {e}")

# Main Logic
def main():
    print("Fetching GPS data every 10 seconds...")
    ser = init_serial()  # Initialize serial connection

    try:
        while True:
            print("\n--- Fetching GPS Data ---")
            gps_data=receive_data(ser)  # Receive and process GPS data
            if gps_data:
                print(gps_data)
            time.sleep(10)     # Wait for 10 seconds
    except KeyboardInterrupt:
        print("\nExiting program...")
    finally:
        ser.close()  # Close serial connection

if __name__ == "__main__":
    main()