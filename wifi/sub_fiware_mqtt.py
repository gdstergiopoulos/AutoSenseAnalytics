import requests
from requests.structures import CaseInsensitiveDict

url = "http://150.140.186.118:1026/v2/subscriptions"



def subscribe_entity_to_mqtt(fiware_service_path, entity_id,entity_type,update_attr,mqtt_topic):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Fiware-ServicePath"] = "%s"%fiware_service_path  
    data="""{
                "description": "subscription for entity %s",
                "subject": {
                    "entities": [
                        {
                            "id": "%s",
                            "type": "%s"
                        }
                    ],
                    "condition": {
                        "attrs": [
                            "%s"
                        ]
                    }
                },
                "notification": {
                    "mqtt": {
                        "url": "mqtt://150.140.186.118:1883",
                        "topic": "autosense/%s"
                    }
                }
            }"""%(entity_id,entity_id,entity_type,update_attr,mqtt_topic)
    response = requests.post(url, headers=headers, data=data)
    print(response.status_code)
    print(response.text)
    
#demo entity 
#DO THIS FOR EVERY CAR (ONLY car0 exists)
# subscribe_entity_to_mqtt("/AutoSenseAnalytics/demo","car0","car_measurements","timestamp","demo")
#4g entity
# subscribe_entity_to_mqtt("/AutoSenseAnalytics","4G_Measurement","4G","rssi","4g_rssi")

subscribe_entity_to_mqtt("/AutoSenseAnalytics","IMU_avg","Demo","accx","imuavg")


# data = """
# { 
#   "description": "TEST2", 
#   "subject": { 
#     "entities": [ 
#       { 
#         "id": "car0", 
#         "type": "car_measurements" 
#       } 
#     ],
#     "condition": {
#       "attrs": [
#         "timestamp"
#       ]
#     }
#   }, 
#   "notification": {
#     "mqtt": {
#       "url": "mqtt://150.140.186.118:1883",
#       "topic": "autosense/demo"
#     }
#   }
# }
# """

# resp = requests.post(url, headers=headers, data=data)
# print(resp.status_code)
# print(resp.text)