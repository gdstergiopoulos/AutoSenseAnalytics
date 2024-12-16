import subprocess
from datetime import datetime

# Generate a unique filename based on timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"image_{timestamp}.jpg"

# Use libcamera-jpeg to capture the image
try:
    print("Capturing image...")
    subprocess.run(["libcamera-jpeg", "-o", filename, "--width", "1920", "--height", "1080"], check=True)
    print(f"Image saved as {filename}")
except subprocess.CalledProcessError as e:
    print(f"Error capturing image: {e}")
