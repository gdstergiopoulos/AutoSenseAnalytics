import serial
import time

def get_gps_coordinates():
    # Open serial port
    ser = serial.Serial('/dev/ttyUSB2', baudrate=9600, timeout=1)
    
    # Send AT command to turn on GPS
    ser.write(b'AT+CGNSPWR=1\r')
    time.sleep(1)
    
    # Send AT command to get GPS data
    ser.write(b'AT+CGNSINF\r')
    time.sleep(1)
    
    # Read response
    response = ser.read(ser.inWaiting()).decode('utf-8')
    
    # Close serial port
    ser.close()
    
    # Parse GPS data
    if '+CGNSINF: ' in response:
        gps_data = response.split('+CGNSINF: ')[1].split(',')
        print(gps_data)
        if gps_data[1] == '1':
            latitude = gps_data[3]
            longitude = gps_data[4]
            return latitude, longitude
        else:
            return None, None
    else:
        return None, None

if __name__ == "__main__":
    lat, lon = get_gps_coordinates()
    if lat and lon:
        print(f"Latitude: {lat}, Longitude: {lon}")
    else:
        print("Failed to get GPS coordinates")