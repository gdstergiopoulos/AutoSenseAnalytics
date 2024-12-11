import json

import paho.mqtt.client as mqtt

# Define the MQTT broker details
broker = "150.140.186.118"
port = 1883
topic = "Asset tracking/dragino-lora-gps:1"

# Define the callback function for when a message is received
def on_message(client, userdata, message):
    print(f"Received message: {message.payload.decode()} on topic {message.topic}")
    
    with open("./test.json", "a") as file:
        json.dump({"topic": message.topic, "payload": message.payload.decode()}, file)
        file.write("\n")

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
