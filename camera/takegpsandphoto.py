import subprocess
from datetime import datetime
from PIL import Image, ExifTags
import serial
import time
from get_location_without_class import fetch_gps_data


def embed_gps_metadata(image_path, latitude, longitude):
    try:
        img = Image.open(image_path)
        exif_data = img.info.get("exif", {})
        gps_info = {}

        # Convert latitude and longitude to EXIF GPS format
        gps_info[1] = "N" if latitude >= 0 else "S"
        gps_info[2] = (
            (abs(int(latitude)), 1),
            (int((abs(latitude) % 1) * 60), 1),
            (int(((abs(latitude) * 60) % 1) * 60 * 10000), 10000),
        )
        gps_info[3] = "E" if longitude >= 0 else "W"
        gps_info[4] = (
            (abs(int(longitude)), 1),
            (int((abs(longitude) % 1) * 60), 1),
            (int(((abs(longitude) * 60) % 1) * 60 * 10000), 10000),
        )

        # Add GPS data to the EXIF dictionary
        exif_data["GPSInfo"] = gps_info

        # Save the image with updated metadata
        img.save(image_path, exif=exif_data)
        print(f"GPS metadata embedded: Latitude={latitude}, Longitude={longitude}")
    except Exception as e:
        print(f"Error embedding GPS metadata: {e}")

# Main script
def main():
    # Step 1: Fetch GPS data
    print("Fetching GPS data...")
    latitude, longitude = fetch_gps_data()
    print(f"GPS Data: Latitude={latitude}, Longitude={longitude}")

    # Step 2: Capture photo with libcamera-jpeg
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"image_{timestamp}.jpg"
    print("Capturing image...")
    try:
        subprocess.run(["libcamera-jpeg", "-o", filename, "--width", "1920", "--height", "1080"], check=True)
        print(f"Image saved as {filename}")

        # Step 3: Embed GPS metadata into the photo
        embed_gps_metadata(filename, latitude, longitude)
    except subprocess.CalledProcessError as e:
        print(f"Error capturing image: {e}")

if __name__ == "__main__":
    main()