# Description: Python script to create a subscription in FIWARE Orion Context Broker (it acts as an mqtt client)

import requests
import json

# FIWARE Context Broker details
fiware_url = "http://150.140.186.118:1026"  # Replace with your FIWARE Orion URL
mqtt_broker_url = "http://150.140.186.118:1883"  # Replace with your MQTT broker's IP address #only access through campus network?????
mqtt_topic = "fiware/updates"  # Topic where notifications will be sent
entity_id = "elenishome"  # Replace with your FIWARE entity ID
entity_type = "Device"  # Replace with your FIWARE entity type

# Headers for FIWARE API requests
headers = {
    "Content-Type": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics/Wifi"  # Replace with your FIWARE service path
}

# Define the subscription payload
subscription_payload = {
    "description": "Notify MQTT broker on FIWARE entity updates",
    "subject": {
        "entities": [
            {
                "id": entity_id,
                "type": entity_type
            }
        ],
        "condition": {
            "attrs": ["rssi", "macAddress", "location", "timestamp"]  # Attributes to monitor
        }
    },
    "notification": {
        "endpoint": {
            "uri": f"{mqtt_broker_url}/{mqtt_topic}",  # MQTT broker topic
            "accept": "application/json",
            "type": "MQTT"  # Notify via MQTT
        },
        "attrs": ["rssi", "macAddress", "location", "timestamp"],  # Attributes included in notification
        "metadata": ["dateCreated", "dateModified"]  # Optional metadata
    },
    "throttling": 1  # Minimum interval between notifications
}

# Function to create the subscription
def create_subscription():
    try:
        response = requests.post(fiware_url, headers=headers, json=subscription_payload)
        if response.status_code == 201:
            print("Subscription created successfully!")
            print(json.dumps(response.json(), indent=4))
        else:
            print(f"Failed to create subscription. HTTP Status: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error creating subscription: {e}")

# Main execution
if __name__ == "__main__":
    create_subscription()
