import serial
import time

def main():
    # Specify the USB port where the Arduino is connected.
    # Replace '/dev/ttyUSB0' with your actual port if different.
    arduino_port = '/dev/ttyACM0'
    baud_rate = 9600  # Ensure this matches the Arduino's Serial.begin() value

    try:
        # Initialize serial connection
        print(f"Connecting to Arduino on {arduino_port} at {baud_rate} baud...")
        ser = serial.Serial(arduino_port, baud_rate, timeout=1)
        time.sleep(2)  # Wait for the connection to initialize

        print("Connected! Reading data...\nPress Ctrl+C to stop.")

        # Read data in a loop
        while True:
            if ser.in_waiting > 0:  # Check if data is available
                line = ser.readline().decode('utf-8').strip()  # Read a line and decode it
                print(f"Received: {line}")

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
