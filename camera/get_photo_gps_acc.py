import subprocess
from datetime import datetime
from PIL import Image, ExifTags
import serial
import time
from getlocationfrom4Ghat import *
from get_acceleration import *
import piexif

def embed_gps_metadata(image_path, latitude, longitude):
    try:
        # Convert latitude and longitude to EXIF GPS format
        gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef: "N" if latitude >= 0 else "S",
            piexif.GPSIFD.GPSLatitude: [
                (abs(int(latitude)), 1),
                (int((abs(latitude) % 1) * 60), 1),
                (int(((abs(latitude) * 60) % 1) * 60 * 10000), 10000),
            ],
            piexif.GPSIFD.GPSLongitudeRef: "E" if longitude >= 0 else "W",
            piexif.GPSIFD.GPSLongitude: [
                (abs(int(longitude)), 1),
                (int((abs(longitude) % 1) * 60), 1),
                (int(((abs(longitude) * 60) % 1) * 60 * 10000), 10000),
            ],
        }

        # Load the image and existing EXIF data
        exif_dict = {"GPS": gps_ifd}

    ## Add timestamp to the exif_dict this is how will this be done
    #      exif_dict = {
    #     "GPS": {
    #         gps_ifd
    #     },
    #     "Exif": {
    #         piexif.ExifIFD.DateTimeOriginal: timestamp.encode(), ##NEED TO REPLACE
    #     }
    # }
        
        exif_bytes = piexif.dump(exif_dict)

        # Write EXIF metadata to the image
        img = Image.open(image_path)
        img.save(image_path, exif=exif_bytes)
        print(f"GPS metadata embedded: Latitude={latitude}, Longitude={longitude}")
    except Exception as e:
        print(f"Error embedding GPS metadata: {e}")


# Main script
def main():
    while True:
        # Get location from 4g hAT and keep only the latitude and longitude
        print("Fetching GPS data...")
        latitude, longitude = get_gps_location()
        print(f"GPS Data: Latitude={latitude}, Longitude={longitude}")

        #Get timestamp
        timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")

        #Get accelerometer data


        #Capture photo with libcamera-jpeg
        filename = f"image_{timestamp}.jpg"
        print("Capturing image...")

        try:
            subprocess.run(["libcamera-jpeg", "-o", filename, "--width", "1920", "--height", "1080"], check=True)
            print(f"Image saved as {filename}")

            # Step 3: Embed GPS metadata into the photo
            embed_gps_metadata(filename, latitude, longitude)
        except subprocess.CalledProcessError as e:
            print(f"Error capturing image: {e}")
            time.sleep(10)


if __name__ == "__main__":

    main()