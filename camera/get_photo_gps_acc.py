import subprocess
from datetime import datetime
from PIL import Image, ExifTags
import serial
import time
from getlocationfrom4Ghat import *
from get_acceleration import *
import piexif
import requests 


serial_port = "/dev/ttyUSB2"  
baud_rate = 115200




def add_metadata(image_path, latitude, longitude, timestamp):
    try:# Open the image
        img = Image.open(image_path)

        # Convert latitude and longitude to EXIF format (Degrees, Minutes, Seconds)
        def to_dms(value):
            degrees = int(value)
            minutes = int((value - degrees) * 60)
            seconds = (value - degrees - minutes / 60) * 3600
            return ((degrees, 1), (minutes, 1), (int(seconds * 100), 100))

        lat_dms = to_dms(abs(latitude))
        lon_dms = to_dms(abs(longitude))

        # Determine latitude and longitude reference
        lat_ref = "N" if latitude >= 0 else "S"
        lon_ref = "E" if longitude >= 0 else "W"

        # Prepare EXIF data
        exif_dict = {
            "GPS": {
                piexif.GPSIFD.GPSLatitudeRef: lat_ref.encode(),
                piexif.GPSIFD.GPSLatitude: lat_dms,
                piexif.GPSIFD.GPSLongitudeRef: lon_ref.encode(),
                piexif.GPSIFD.GPSLongitude: lon_dms,
            },
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: timestamp.encode(),
            }
        }

        # Insert the EXIF data into the image
        exif_bytes = piexif.dump(exif_dict)
        img.save(image_path, exif=exif_bytes)  # Overwrites the original file
        print(f"Metadata added to {image_path}\n\n")
    except Exception as e:
        print(f"Error adding metadata: {e}")


def upload_photo(filename,accx,accy,accz):
    image_path = f"camera/{filename}"
    with open(image_path, 'rb') as photo:
        files = {'photo': photo}
        data = {
            'accx': accx,
            'accy': accy,
            'accz': accz
        }
        response = requests.post('http://150.140.186.118:4943/upload', files=files, data=data)
        if response.status_code == 200 or response.status_code == 201:
            print("Upload successful:", response.json())
        else:
            print("Failed to upload:", response.status_code, response.text)


def main():
    while True:
        print("Fetching GPS data...")
        data=get_gps_location(serial_port, baud_rate)
        print(data)
        latitude, longitude = get_gps_location(serial_port, baud_rate)
        print(f"GPS Data: Latitude={latitude}, Longitude={longitude}")
        if latitude and longitude:
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  

            ax, ay, az = get_acceleration()

            if ax and ay and az:
                filename = f"image_{timestamp}.jpg"
                print("Capturing image...")

                try:
                    subprocess.run(["libcamera-jpeg", "-o", filename, "--width", "1920", "--height", "1080"], check=True)
                    print(f"Image saved as {filename}")

                    add_metadata(filename, latitude, longitude, timestamp)
                    upload_photo(filename, ax, ay, az)
                except subprocess.CalledProcessError as e:
                    print(f"Error capturing image: {e}")
                    time.sleep(10)


if __name__ == "__main__":

    main()