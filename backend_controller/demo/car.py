import random 
from datetime import datetime,timezone
import requests
from entity_init import create_entity


class Car:
    def __init__(self,car_id):
        self.car_id = car_id
        self.battery=random.uniform(70,100)
        self.counter=0

        #maybe re-think, how the path is generated (too small now)
        self.path= requests.get('http://localhost:5000/path/'+str(car_id)).json()
        
        # print(self.path[0]['path'][0]['lat'])
        self.path_len=len(self.path[0]['path'])
        # print(self.path_len)
        self.lat=self.path[0]['path'][0]['lat']
        self.lon=self.path[0]['path'][0]['lon']

        #check if entity exists or create one
        response=requests.get('http://150.140.186.118:1026/v2/entities/car'+str(self.car_id))
       
        if response.status_code == 200:
            print(f"Entity  already exists.")
        elif response.status_code == 404:
            print(f"Entity does not exist.")
            create_entity(self.car_id)
            print(f"Entity created.")
        else:
            print(f"Error checking entity: {response.status_code}")



        
    def generate_data(self):
        self.battery=max(0,self.battery-0.1)
        self.counter+=1
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
                    "coordinates": [self.path[0]['path'][(self.counter) % self.path_len]['lon'], self.path[0]['path'][(self.counter) % self.path_len]['lat']]
                }
            },
            "speed": {
                "type": "Number",
                "value": random.uniform(20,80)
            },
            "rssi_cellular": {
                "type": "Number",
                "value": random.uniform(-120,-50)
            },
            "rssi_wifi": {
                "type": "Number",
                "value": random.uniform(-90,-30)
            },
            "rssi_lora": {
                "type": "Number",
                "value": random.uniform(-140,-80)
            },
            "imu_roughness": {
                "type": "Number",
                "value": random.uniform(0,1)
            },
            "camera": {
                "type": "URL",
                "value": self.get_random_pic()
            }
            }
        
    def get_random_pic(self):
        pics=requests.get('http://150.140.186.118:4943/api/photos').json()
        numofpics=len(pics)
        photo_src="http://150.140.186.118:4943/photo/"+str(random.randint(1,numofpics))
        return photo_src
    
    def post_data(self):
        headers={
            "Content-Type": "application/json",
            "FIWARE-ServicePath": "/AutoSenseAnalytics/demo"
        }
        url = "http://150.140.186.118:1026/v2/entities/car"+str(self.car_id)+"/attrs"
        
        data=self.generate_data()
        self.patch_measument(data,url,headers)
    
    def patch_measument(self,measurement,fiware_url, headers): 
        try:
            response = requests.patch(fiware_url, headers=headers, json=measurement)
            response.raise_for_status()
            print("Measurement patched successfully.")
        except requests.exceptions.HTTPError as err:
            print(f"Failed to patch measurement: {err}")
        return 0





    
    
