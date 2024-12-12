import ast
import json

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
    """
    Creates a JSON object in the specified format without the macAddress field.
    """
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

# Direct program execution
file_path = "11_12_measurements.json"  # Replace with the actual file path
# formatted_measurements = []

# Open the file and process it
with open(file_path, "r") as file:
    # Load the file as JSON (assume it's an array of measurement dictionaries)
    # Process each row in the file
    for line in file:
        try:
            # Extract measurements from the current row
            entry = json.loads(line.strip())
            rssi, timestamp, location = extract_measurements(entry)

            # Format the extracted data into JSON
            formatted_measurement = create_json(rssi, timestamp, location)

            # Add the formatted measurement to the list
            print(formatted_measurement)

        except RuntimeError as e:
            # Handle errors for specific rows
            print("Error processing row:", e)

