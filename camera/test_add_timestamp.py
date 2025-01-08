from PIL import Image
import piexif
import datetime

def add_metadata(image_path, output_path, latitude, longitude, timestamp):
    # Open the image
    img = Image.open(image_path)

    # Convert latitude and longitude to EXIF format
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
    img.save(output_path, exif=exif_bytes)
    print(f"Metadata added to {output_path}")

# Example usage
if __name__ == "__main__":
    input_image = "camera/image_20241216_161002.jpg"  # Replace with the path to your image
    output_image = "output_with_metadata.jpg"

    # Example metadata
    latitude = 37.7749  # Latitude of San Francisco
    longitude = -122.4194  # Longitude of San Francisco
    timestamp = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")

    add_metadata(input_image, output_image, latitude, longitude, timestamp)
