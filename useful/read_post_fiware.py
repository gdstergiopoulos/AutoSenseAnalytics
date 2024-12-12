import requests
import ast
import json

# FIWARE Orion Context Broker URL
fiware_url = "http://150.140.186.118:1026/v2/entities"

# Headers for the request
headers = {
    "Content-Type": "application/json",
    "Fiware-ServicePath": "/AutoSenseAnalytics/LoRa" 
}

file_path = "11_12_measurements.json"  


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
        # "id": "LoraMeasurement", only for the first post
        # "type": "rssi",
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


def post_to_fiware(measurement,fiware_url=fiware_url, headers=headers):
    try:
        response = requests.post(fiware_url, headers=headers, json=measurement)
        response.raise_for_status()
        print("Measurement posted successfully.")
    except requests.exceptions.HTTPError as err:
        print(f"Failed to post measurement: {err}")

    return 0

def patch_measument(measurement,fiware_url=fiware_url, headers=headers): #for uploading the measurements
    try:
        response = requests.patch(fiware_url, headers=headers, json=measurement)
        response.raise_for_status()
        print("Measurement patched successfully.")
    except requests.exceptions.HTTPError as err:
        print(f"Failed to patch measurement: {err}")

    return 0


# Open the file and process it
with open(file_path, "r") as file:
    for line in file:
        try:
            # Extract measurements from the current row
            entry = json.loads(line.strip())
            rssi, timestamp, location = extract_measurements(entry)
            # Format the extracted data into JSON
            formatted_measurement = create_json(rssi, timestamp, location)
            if formatted_measurement:
                try:
                    # post_to_fiware(formatted_measurement,fiware_url=fiware_url, headers=headers)
                    patch_measument(formatted_measurement, fiware_url + "/LoraMeasurement/attrs", headers)   
                except:
                    print("Failed to patch measurement")
        except RuntimeError as e:
            # Handle errors for specific rows
            print("Error processing row:", e)

