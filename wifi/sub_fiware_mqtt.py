import requests
from requests.structures import CaseInsensitiveDict

url = "http://150.140.186.118:1026/v2/subscriptions"

headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"
headers["Fiware-ServicePath"] = "/AutoSenseAnalytics/demo"

data = """
{ 
  "description": "TEST2", 
  "subject": { 
    "entities": [ 
      { 
        "id": "car0", 
        "type": "car_measurements" 
      } 
    ],
    "condition": {
      "attrs": [
        "timestamp"
      ]
    }
  }, 
  "notification": {
    "mqtt": {
      "url": "mqtt://150.140.186.118:1883",
      "topic": "autosense/demo"
    }
  }
}
"""

resp = requests.post(url, headers=headers, data=data)
print(resp.status_code)
print(resp.text)