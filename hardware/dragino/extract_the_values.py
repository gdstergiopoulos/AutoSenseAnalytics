import csv
import serial
import time
import re
import datetime

def main():
    # Specify the USB port where the Arduino is connected.
    # Replace '/dev/ttyUSB0' with your actual port if different.
    arduino_port = '/dev/ttyACM0'
    baud_rate = 9600  # Ensure this matches the Arduino's Serial.begin() value


    latitude_pattern = r'Latitude:\s*([\d.]+)'
    longitude_pattern = r'Longitude:\s*([\d.]+)'
    counter_pattern = r'Counter value:\s*(\d+)'


    try:
        # Initialize serial connection
        print(f"Connecting to Arduino on {arduino_port} at {baud_rate} baud...")
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        time.sleep(2)  # Wait for the connection to initialize

        print("Connected! Reading data...\nPress Ctrl+C to stop.")
        
        latitude=longitude=counter_value=None
        cread=False

        # Read data in a loop
        while True:
            if ser.in_waiting > 0:  # Check if data is available
                line = ser.readline().decode('utf-8').strip()  # Read a line and decode it
                print(f"Received: {line}")
                if "Latitude" in line:
                    match = re.search(latitude_pattern, line)
                    if match:
                        latitude = float(match.group(1))
                        print(f"Latitude extracted: {latitude}")

                # Check for Longitude
                if "Longitude" in line:
                    match = re.search(longitude_pattern, line)
                    if match:
                        longitude = float(match.group(1))
                        print(f"Longitude extracted: {longitude}")

                # Check for Counter Value
                if "Counter value" in line:
                    match = re.search(counter_pattern, line)
                    if match:
                        cread=True
                        counter_value = int(match.group(1))
                        print(f"Counter value extracted: {counter_value}")
                
                # Print results when all three are extracted
            if latitude and longitude and cread:
                timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # print("\n--- Extracted Data ---")
                # print(f"Latitude: {latitude}")
                # print(f"Longitude: {longitude}")
                # print(f"Counter Value: {counter_value}")
                # print("-----------------------\n")
                with open('no_signal_measurements.csv', mode='a') as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, latitude, longitude, counter_value])
                    print("\nData written to file.\n")


                latitude=longitude=None
                cread=False
                

    except serial.SerialException as e:
        print(f"Error: {e}")

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        # Close the serial connection if open
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()
