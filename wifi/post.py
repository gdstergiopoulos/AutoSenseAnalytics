import requests
#reverse proxy εδω, ετσι ώστε να μην βλέπουν ολοι το context broker
#το reverse proxy διαβάζει tokens και δίνει τα access
url = "http://150.140.186.118:1026/v2/entities"
headers = {
    "Content-Type": "application/json", #τι απαντηση περιμενω
    
    "FIWARE-ServicePath": "/week4_up1083861"
}

data = {
    "id": "test_noisemeter_up1083861", #το id του entity
    "type": "noisemeter",
    "noise": {
        "type": "Number",
        "value": 30.0
    }
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 201:
    print("Entity created successfully with service and path!")
else:
    print(f"Failed to create entity: {response.status_code}")
    print(response.json())
