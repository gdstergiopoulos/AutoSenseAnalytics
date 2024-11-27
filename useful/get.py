import requests


url = "http://150.140.186.118:1026/v2/entities/wifi_rssi/attrs"
headers = {
    "Accept": "application/json",
    
    "FIWARE-ServicePath": "/week4_testteam04"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    entity = response.json()
    print("Full entity with service and path:")
    print(entity)
    print("\nNoise attribute value:")
    print(entity["noise"]["value"])
else:
    print(f"Failed to retrieve entity: {response.status_code}")
    print(response.json())
