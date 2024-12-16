import requests
import ast
import json
import paho.mqtt.client as mqtt

# FIWARE Orion Context Broker URL
fiware_url = "http://150.140.186.118:1026/v2/entities"

#mqtt connection details
broker = '150.140.186.118'
port = 1883
topic='Asset tracking/dragino-lora-gps:1'

# Headers for the request
headers = {
    "Content-Type": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics/LoRa"
}

def extract_measurements(entry):
    """
    Extracts the required measurements from a single row in the file.
    """
    try:
        # Extract the 'payload' field and evaluate it as a dictionary
        raw_payload = entry['payload']
        cleaned_payload = ast.literal_eval(raw_payload)

        # Extract the required data
        timestamp = cleaned_payload['time']
        latitude = cleaned_payload['object']['location']['latitude']
        longitude = cleaned_payload['object']['location']['longitude']
        location = [longitude, latitude]  # GeoJSON format uses [longitude, latitude]
        rssi = cleaned_payload['rxInfo'][0]['rssi']

        return rssi, timestamp, location

    except (ValueError, KeyError) as e:
        raise RuntimeError(f"Error processing entry: {str(e)}")


def create_json(rssi, timestamp, location):
    measurement = {
        "rssi": {
            "value": rssi,
            "type": "Number"
        },
        "location": {
            "value": {
                "type": "Point",
                "coordinates": location
            },
            "type": "geo:json"
        },
        "timestamp": {
            "value": timestamp,
            "type": "DateTime"
        }
    }
    return measurement

def patch_measument(measurement,fiware_url=fiware_url, headers=headers): #for uploading the measurements
    try:
        response = requests.patch(fiware_url, headers=headers, json=measurement)
        response.raise_for_status()
        print("Measurement patched successfully.")
    except requests.exceptions.HTTPError as err:
        print(f"Failed to patch measurement: {err}")
    return 0

def validate_coordinates(latitude, longitude):
    """
    Validates latitude and longitude values.
    Latitude must be between -90 and 90.
    Longitude must be between -180 and 180.
    """
    if -90 <= latitude <= 90 and -180 <= longitude <= 180:
        return True
    return False


# Define the callback function for when a message is received
def on_message(client, userdata, message):
    try:
        # print(f"Received message: {message.payload.decode()} on topic {message.topic}")
        curr= {"topic": message.topic, "payload": message.payload.decode()}
        rssi,timestamp,location = extract_measurements(curr)
        latitute = location[1]
        longitude = location[0]
        if not validate_coordinates(latitute,longitude):
            print("Invalid coordinates")
        else:
            formatted_measurement = create_json(rssi, timestamp, location)
            patch_measument(formatted_measurement,fiware_url,headers)
            print(formatted_measurement)
    except Exception as e:
        print(f"Error processing entry: {str(e)}")
    
  
    
    

# Create an MQTT client instance
client = mqtt.Client()

# Assign the on_message callback function
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker, port)

# Subscribe to the topic
client.subscribe(topic)

# Start the MQTT client loop to process network traffic and dispatch callbacks
client.loop_forever()
