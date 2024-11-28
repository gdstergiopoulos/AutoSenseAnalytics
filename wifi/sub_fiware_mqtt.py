import requests
from requests.structures import CaseInsensitiveDict

url = "http://150.140.186.118:1026/v2/subscriptions"

headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"
headers["Fiware-ServicePath"] = "/AutoSenseAnalytics/Wifi"

data = """
{ 
  "description": "TEST2", 
  "subject": { 
    "entities": [ 
      { 
        "id": "elenishome", 
        "type": "rssi_bssid" 
      } 
    ],
    "condition": {
      "attrs": [
        "rssi"
      ]
    }
  }, 
  "notification": {  
    "http": {
      "url": "https://autosenseanalytics.azurewebsites.net/wakeup",
      "method": "GET"
    },
    "mqtt": {
      "url": "mqtt://150.140.186.118:1883",
      "topic": "autosense/wifi"
    }
  }
}
"""

resp = requests.post(url, headers=headers, data=data)
print(resp.status_code)
print(resp.text)