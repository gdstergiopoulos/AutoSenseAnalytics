import requests
import random

url = "http://150.140.186.118:1026/v2/entities/test_noisemeter_up1083861/attrs"
headers = {
    "Content-Type": "application/json",
    
    "FIWARE-ServicePath": "/week4_up1083861"
}

data = {
    "noise": {
        "type": "Number",
        "value": random.uniform(32, 33)
    }
}

response = requests.patch(url, json=data, headers=headers)

if response.status_code == 204:
    print("Entity updated successfully with service and path!")
else:
    print(f"Failed to update entity: {response.status_code}")
    print(response.json())
