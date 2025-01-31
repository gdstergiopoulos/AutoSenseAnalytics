import random 
from datetime import datetime,timezone
import requests
class Car:
    def __init__(self,car_id):
        self.car_id = car_id
        self.battery=random.uniform(70,100)
        self.path= requests.get('http://localhost:5000/path/'+str(car_id)).json()
        self.counter=0
        # print(self.path[0]['path'][0]['lat'])
        self.path_len=len(self.path[0]['path'])
        # print(self.path_len)
        self.lat=self.path[0]['path'][0]['lat']
        self.lon=self.path[0]['path'][0]['lon']

        
    def generate_data(self):
        self.battery_level=max(0,self.battery-0.8)
        self.counter+=1
        return {
            "car_id": self.car_id,
            "battery": self.battery_level,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "location":{
                "lat": self.path[0]['path'][(self.counter) % self.path_len]['lat'],
                "lon": self.path[0]['path'][(self.counter) % self.path_len]['lon']
            },
            "speed": random.uniform(20,80),
            "rssi_cellular": random.uniform(-120,-50),
            "rssi_wifi": random.uniform(-90,-30),
            "rssi_lora": random.uniform(-140,-80),
            "imu_roughness": random.uniform(0,1),
            "camera": self.get_random_pic()
        }
    
    def get_random_pic(self):
        pics=requests.get('http://150.140.186.118:4943/api/photos').json()
        numofpics=len(pics)
        photo_src="http://150.140.186.118:4943/photos/"+str(random.randint(1,numofpics))
        return photo_src
    

    
    
