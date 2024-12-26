from PIL import Image
import exifread
import requests

SERVER_URL = 'http://localhost:3000/upload_photo'

def get_exif_data(image_path):
    with open(image_path, 'rb') as image_file:
        tags = exifread.process_file(image_file)
        
        lat = None
        lon = None
        timestamp = None
        
        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            lat = tags['GPS GPSLatitude']
            lon = tags['GPS GPSLongitude']
        
        if 'EXIF DateTimeOriginal' in tags:
            timestamp = tags['EXIF DateTimeOriginal']
        
        return lat, lon, timestamp

def convert_to_degrees(value):
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)
    
    return d + (m / 60.0) + (s / 3600.0)

# Upload the photo and metadata
def upload_photo(photo_path, lat, lon, timestamp):
    with open(photo_path, 'rb') as photo:
        files = {'photo': photo}
        data = {
            'lat': lat,
            'lon': lon,
            'timestamp': timestamp
        }
        response = requests.post(SERVER_URL, files=files, data=data)

        if response.status_code == 200:
            print("Upload successful:", response.json())
        else:
            print("Failed to upload:", response.status_code, response.text)


def main():
    image_path = 'camera/image_20241216_161530.jpg'
    lat, lon, timestamp = get_exif_data(image_path)
    
    if lat and lon:
        lat = convert_to_degrees(lat)
        lon = convert_to_degrees(lon)
    
    print(f"Latitude: {lat}, Longitude: {lon}, Timestamp: {timestamp}")
    if(timestamp is None):
        timestamp = "2024-12-16 16:15:30"
    upload_photo(image_path, lat, lon, timestamp)
    #post the lat, lon and photo to the server
    
    
    



if __name__ == "__main__":
    main()
