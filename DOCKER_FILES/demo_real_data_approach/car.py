import random 
from datetime import datetime
import requests
from entity_init import create_entity
import math 

class Car:
    def __init__(self, car_id,location="center"):
        self.car_id = car_id
        self.battery = random.uniform(70, 100)
        self.counter = 0
        
        # Fetch path data
        self.data = requests.get('http://150.140.186.118:7101/api/measurements/4g/'+str(location)).json()
        self.path_len = len(self.data)
        
        # Initialize a random starting position
        self.current_index = random.randint(0, self.path_len - 1)  # Random index from the data list

        print(f"Car {self.car_id} starting position: {self.data[self.current_index]['latitude']}, {self.data[self.current_index]['longitude']}")
        
        # Check if entity exists or create one
        response = requests.get(f'http://150.140.186.118:1026/v2/entities/car{self.car_id}')
        if response.status_code == 200:
            print(f"Entity already exists.")
        elif response.status_code == 404:
            print(f"Entity does not exist.")
            create_entity(self.car_id)
            print(f"Entity created.")
        else:
            print(f"Error checking entity: {response.status_code}")

    def generate_data(self):
        # Update battery level
        self.battery = max(0, self.battery - 0.1)
        if (self.battery==0):
            self.battery = random.uniform(70, 100)

        # Iterate to the next data point
        self.current_index = (self.current_index + 1) % self.path_len  # Move to the next position in a circular manner
        
        # Generate the data payload
        return {
            "battery": {
                "type": "Number",
                "value": self.battery
            },
            "timestamp": {
                "type": "DateTime",
                "value": datetime.now().isoformat()
            },
            "location": {
                "type": "geo:json",
                "value": {
                    "type": "Point",
                    "coordinates": [
                        self.data[self.current_index]['longitude'], 
                        self.data[self.current_index]['latitude']
                    ]
                }
            },
            "speed": {
                "type": "Number",
                "value": random.uniform(20, 80)
            },
            "rssi_cellular": {
                "type": "Number",
                "value": self.data[self.current_index]['rssi']
            },
            "rssi_wifi": {
                "type": "Number",
                "value": random.uniform(-90, -30)
            },
            "rssi_lora": {
                "type": "Number",
                "value": random.uniform(-140, -80)
            },
            "imu_roughness": {
                "type": "Number",
                "value": random.uniform(0, 1)
            },
            "camera": {
                "type": "URL",
                "value": self.get_closest_photo(self.data[self.current_index]['latitude'], self.data[self.current_index]['longitude'])
            }
        }

    def get_random_pic(self):
        pics = requests.get('http://150.140.186.118:4943/api/photos').json()
        numofpics = len(pics)
        photo_src = f"http://150.140.186.118:4943/photo/{random.randint(1, numofpics)}"
        return photo_src
    
    

    def get_closest_photo(self,lat, lon):
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Radius of the Earth in km
            
            lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            
            return R * c  # Distance in km
        
        try:
            photos = requests.get('http://150.140.186.118:4943/api/photos').json()
            
            if not photos:
                return None  # No photos available
            
            closest_photo = min(photos, key=lambda photo: haversine(lat, lon, photo['latitude'], photo['longitude']))
            
            return f"http://150.140.186.118:4943/photo/{closest_photo['id']}"
        except Exception as e:
            print(f"Error fetching closest photo: {e}")
            return None

    def post_data(self):
        headers = {
            "Content-Type": "application/json",
            "FIWARE-ServicePath": "/AutoSenseAnalytics/demo"
        }
        url = f"http://150.140.186.118:1026/v2/entities/car{self.car_id}/attrs"
        
        data = self.generate_data()
        self.patch_measument(data, url, headers)
    
    def patch_measument(self, measurement, fiware_url, headers): 
        try:
            response = requests.patch(fiware_url, headers=headers, json=measurement)
            response.raise_for_status()
            print("Measurement patched successfully.")
        except requests.exceptions.HTTPError as err:
            print(f"Failed to patch measurement: {err}")
        return 0
