import subprocess
from datetime import datetime
from PIL import Image, ExifTags
import serial
import time
from getlocationfrom4Ghat import *
from get_acceleration import *
import piexif


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
        print(f"Metadata added to {image_path}")
    except Exception as e:
        print(f"Error adding metadata: {e}")


def main():
    while True:
        # Get location from 4g hAT and keep only the latitude and longitude
        print("Fetching GPS data...")
        latitude, longitude = get_gps_location(serial_port, baud_rate)
        print(f"GPS Data: Latitude={latitude}, Longitude={longitude}")
        if latitude and longitude:
            #Get timestamp
            timestamp = datetime.now().strftime("%Y:%m:%d %H:%M:%S")

            #Get accelerometer data
            ax, ay, az = get_acceleration()

            if ax and ay and az:
                #Capture photo with libcamera-jpeg
                filename = f"image_{timestamp}.jpg"
                print("Capturing image...")

                try:
                    subprocess.run(["libcamera-jpeg", "-o", filename, "--width", "1920", "--height", "1080"], check=True)
                    print(f"Image saved as {filename}")

                    # Step 3: Embed GPS metadata into the photo
                    add_metadata(filename, latitude, longitude, timestamp)
                except subprocess.CalledProcessError as e:
                    print(f"Error capturing image: {e}")
                    time.sleep(10)


if __name__ == "__main__":

    main()