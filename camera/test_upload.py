import requests

def upload_photo():
    image_path='camera/output_with_metadata.jpg'
    with open(image_path, 'rb') as photo:
        files = {'photo': photo}
        data = {
            'accx': 0.5,
            'accy': 0,
            'accz': 0
        }
        response = requests.post('http://150.140.186.118:4943/upload', files=files, data=data)
        if response.status_code == 200 or response.status_code == 201:
            print("Upload successful:", response.json())
        else:
            print("Failed to upload:", response.status_code, response.text)

upload_photo()