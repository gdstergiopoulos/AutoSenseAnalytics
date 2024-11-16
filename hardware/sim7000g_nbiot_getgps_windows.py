import serial
import time

def send_at_command(ser, command, timeout=1):
    ser.write((command + '\r\n').encode())
    time.sleep(timeout)
    response = ser.read_all().decode()
    return response

def get_gps_coordinates():
    ser = serial.Serial('COM9', 115200, timeout=1)
    
    # Initialize GPS
    send_at_command(ser, 'AT+CGNSPWR=1')
    time.sleep(2)
    
    # Get GPS data
    response = send_at_command(ser, 'AT+CGNSINF')
    
    # Close serial port
    ser.close()
    
    # Parse GPS data
    if '+CGNSINF: ' in response:
        gps_data = response.split('+CGNSINF: ')[1].split(',')
        if gps_data[1] == '1':
            latitude = gps_data[3]
            longitude = gps_data[4]
            return latitude, longitude
        else:
            return 'GPS not fixed'
    else:
        return 'Error retrieving GPS data'

if __name__ == '__main__':
    coords = get_gps_coordinates()
    print('GPS Coordinates:', coords)