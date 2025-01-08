from flask import Flask, request, send_file, jsonify
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import sqlite3
from werkzeug.utils import secure_filename
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "./uploads"
DATABASE = "./photos.db"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS photos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        timestamp TEXT,
                        latitude REAL,
                        longitude REAL,
                        accx REAL,
                        accy REAL,
                        accz REAL,
                        path TEXT NOT NULL
                      )''')
    conn.commit()
    conn.close()

init_db()

# Function to extract GPS and timestamp metadata
def extract_metadata(filepath):
    metadata = {
        "timestamp": None,
        "latitude": None,
        "longitude": None,
    }
    try:
        with Image.open(filepath) as img:
            info = img._getexif()
            if info:
                for tag, value in info.items():
                    tag_name = TAGS.get(tag, tag)
                    if tag_name == "DateTimeOriginal":
                        metadata["timestamp"] = value
                    elif tag_name == "GPSInfo":
                        gps_data = {}
                        for t in value:
                            sub_tag = GPSTAGS.get(t, t)
                            gps_data[sub_tag] = value[t]

                        # Extract latitude and longitude if available
                        if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
                            lat = gps_data["GPSLatitude"]
                            lat_ref = gps_data["GPSLatitudeRef"]
                            metadata["latitude"] = convert_to_degrees(lat)
                            if lat_ref != "N":
                                metadata["latitude"] = -metadata["latitude"]

                        if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
                            lon = gps_data["GPSLongitude"]
                            lon_ref = gps_data["GPSLongitudeRef"]
                            metadata["longitude"] = convert_to_degrees(lon)
                            if lon_ref != "E":
                                metadata["longitude"] = -metadata["longitude"]
    except Exception as e:
        print(f"Error extracting metadata: {e}")
    return metadata

# Helper function to convert GPS coordinates to degrees
def convert_to_degrees(value):
    d, m, s = value
    return d + (m / 60.0) + (s / 3600.0)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message":"Welcome to the photo API! Up and running"})



@app.route("/upload", methods=["POST"])
def upload_photo():
    if "photo" not in request.files:
        return jsonify({"error": "No photo file provided"}), 400

    photo = request.files["photo"]
    if photo.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(photo.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    photo.save(filepath)

    metadata = extract_metadata(filepath)
    filepath = "./uploads/" + filename
    # Simulate accelerometer data
    # accx = random.uniform(-10, 10)
    # accy = random.uniform(-10, 10)
    # accz = random.uniform(-10, 10)

    # Ensure the accelerometer data is provided and valid
    # if not all(param in request.form for param in ["accx", "accy", "accz"]):
    #     return jsonify({"error": "Missing accelerometer data"}), 400

    try:
        accx = float(request.form["accx"])
        accy = float(request.form["accy"])
        accz = float(request.form["accz"])
    except (ValueError,TypeError):
        accx = None
        accy = None
        accz = None

    # Save metadata and file path to the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO photos (filename, timestamp, latitude, longitude, accx, accy, accz, path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (filename, metadata["timestamp"], metadata["latitude"], metadata["longitude"], accx, accy, accz, filepath))
    conn.commit()
    photo_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Photo uploaded successfully", "id": photo_id,"timestamp":metadata["timestamp"],"latitude":metadata["latitude"],"longitude":metadata["longitude"],"accx":accx}), 201

@app.route("/photo/<int:photo_id>", methods=["GET"])
def fetch_photo(photo_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM photos WHERE id = ?", (photo_id,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return jsonify({"error": "Photo not found"}), 404

    filepath = result[0]
    # if not os.path.exists(filepath):
    #     return jsonify({"error": "File not found on server"}), 404
    if not filepath:
        return jsonify({"error": "File not found on server"}), 404
    
    return send_file(filepath)

@app.route("/photo/delete/<int:photo_id>", methods=["GET"])
def delete_photo(photo_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM photos WHERE id = ?", (photo_id,))
    result = cursor.fetchone()
    if result is None:
        return jsonify({"error": "Photo not found"}), 404

    filepath = result[0]
    if filepath:
        os.remove(filepath)

    cursor.execute("DELETE FROM photos WHERE id = ?", (photo_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Photo deleted successfully"})



@app.route("/api/photos", methods=["GET"])
def get_all_photos():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM photos")
    photos = cursor.fetchall()
    conn.close()

    photos = [
        {
            "id": row[0],
            "filename": row[1],
            "timestamp": row[2],
            "latitude": row[3],
            "longitude": row[4],
            "accx": row[5],
            "accy": row[6],
            "accz": row[7],
            "path": row[8]
        }
        for row in photos
    ]

    return jsonify(photos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4943, debug=True)
