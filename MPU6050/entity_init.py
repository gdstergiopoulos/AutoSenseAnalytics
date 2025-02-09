import requests

url = "http://150.140.186.118:1026/v2/entities"


headers={
    "Content-Type": "application/json",
    "FIWARE-ServicePath": "/AutoSenseAnalytics"
}

def create_entity():
    data={
         "id": "IMU_Measurement",
         "type": "raw",
        "accx": {
            "value": [],
            "type": "Text"
        },
        "accy": {
            "value": [],
            "type": "Text"
        },
        "accz": {
            "value": [],
            "type": "Text"
        },
         "location": {
            "value": {
                "type": "Point",
                "coordinates": [38.230462,21.75315]
            },
            "type": "geo:json"
        },
        "date": {
            "value": "2024-12-18T19:20:56.699Z",
            "type": "DateTime"
        },
        "altitude": {
            "value": 0.5,
            "type": "Number"
        },
        "speed": {
            "value": 0.5,
            "type": "Number"
        }
    }

    response = requests.post(url, json=data, headers=headers)
    print(response)
    if response.status_code == 201:
        print("Entity created successfully with service and path!")
        return 0
    else:
        print(f"Failed to create entity: {response.status_code}")
        print(response.json())
        return 1
    
create_entity()