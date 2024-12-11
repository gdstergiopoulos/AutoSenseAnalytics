import ast  # For safely evaluating dictionary-like strings
import json

# Load the JSON file
with open("testmeasurement.json", "r") as file:
    data = json.load(file)  # Load the outer JSON structure

# Access and clean the 'payload' field
raw_payload = data['payload']

# Process the payload to extract the information
try:
    # Use `ast.literal_eval` to safely evaluate the string as a Python dictionary
    cleaned_payload = ast.literal_eval(raw_payload)

    # Extract the needed information
    latitude = cleaned_payload['object']['location']['latitude']
    longitude = cleaned_payload['object']['location']['longitude']

    # Print the result
    print(f"Latitude: {latitude}, Longitude: {longitude}")
except (ValueError, KeyError) as e:
    print("Error processing the payload:", e)
