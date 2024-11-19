import serial
import time

# Configure the serial port
ser = serial.Serial(
    port='/dev/ttyUSB2',  
    baudrate=115200,
    timeout=1
)

def send_at_command(command, timeout=1):
    ser.write((command + '\r\n').encode())
    time.sleep(timeout)
    response = ser.read(ser.in_waiting).decode()
    return response

def main():
    while True:
        command = input("Enter AT command: ")
        if command.lower() == 'exit':
            break
        response = send_at_command(command)
        print("Response: " + response)

if __name__ == "__main__":
    main()