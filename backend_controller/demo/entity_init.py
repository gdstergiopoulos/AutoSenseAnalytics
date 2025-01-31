import requests

url = "http://150.140.186.118:1026/v2/entities"


headers={
    "Content-Type": "application/json",
    "FIWARE-ServicePath": "/AutoSenseAnalytics/demo"
}

def create_entity(car_id):
    data={
        "id": "car"+str(car_id),
        "type": "car_measurements",
        "battery": {
            "type": "Number",
            "value": 100.0
        },
        "timestamp": {
            "type": "DateTime",
            "value": "2021-05-20T12:00:00Z"
        },
        "location": {
            "type": "geo:json",
            "value": {
                "type": "Point",
                "coordinates": [21.7310443, 38.2435671]
            }
        },
        "speed": {
            "type": "Number",
            "value": 50.0
        },
        "rssi_cellular": {
            "type": "Number",
            "value": -70.0
        },
        "rssi_wifi": {
            "type": "Number",
            "value": -50.0
        },
        "rssi_lora": {
            "type": "Number",
            "value": -90.0
        },
        "imu_roughness": {
            "type": "Number",
            "value": 0.5
        },
        "camera": {
            "type": "URL",
            "value": "http://150.140.186.118:4943/photos/2"
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        print("Entity created successfully with service and path!")
        return 0
    else:
        print(f"Failed to create entity: {response.status_code}")
        print(response.json())
        return 1