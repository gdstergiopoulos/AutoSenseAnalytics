import subprocess
import re
import time
from datetime import datetime

def get_wifi_measurement():
    # Run iwconfig to get the connected WiFi network information
    result = subprocess.run(['iwconfig', 'wlan0'], capture_output=True, text=True)
    output = result.stdout

    # Regular expressions to extract BSSID and RSSI
    bssid_regex = re.compile(r"Access Point: ([\w:]+)")
    rssi_regex = re.compile(r"Signal level=(-?\d+)")

    # Find the BSSID and RSSI in the output
    bssid_match = re.search(bssid_regex, output)
    rssi_match = re.search(rssi_regex, output)

    if bssid_match and rssi_match:
        bssid = bssid_match.group(1)  # Extract the MAC (BSSID)
        rssi = int(rssi_match.group(1))  # Extract the signal strength (RSSI)
        #timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())  # Get the current timestamp
        timestamp = datetime.now().isoformat()
        # return {"BSSID": bssid, "RSSI (dBm)": rssi, "Timestamp": timestamp}
        return bssid, rssi, timestamp, [21.753150, 38.230462]
    else:
        return None

# Infinite loop to repeatedly measure every 10 seconds
def get_wifi_print_loop():
    #only for testing
    while True:
        connected_wifi = get_wifi_measurement()
        if connected_wifi:
            print(f"BSSID: {connected_wifi['BSSID']}, RSSI: {connected_wifi['RSSI (dBm)']} dBm, Timestamp: {connected_wifi['Timestamp']}")
        else:
            print("No WiFi connection detected.")
        
        # Wait for 10 seconds before checking again
        time.sleep(10)
