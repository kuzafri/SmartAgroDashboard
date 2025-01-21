from flask import Flask, jsonify, request
from threading import Thread
import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
from datetime import datetime
from bson import CodecOptions, json_util
from flask_cors import CORS

# MongoDB Atlas configuration
MONGO_URI = "mongodb+srv://kuzafri:kuzafri313@conms.i2dnl.mongodb.net/?retryWrites=true&w=majority&appName=conms"
DB_NAME = "SmartAgro"
COLLECTION_NAME = "sensor_data"

# MQTT configuration
MQTT_BROKER = "34.42.195.199"
MQTT_PORT = 1883
MQTT_TOPIC = "SmartAgro"

# Flask application
app = Flask(__name__)
CORS(app)

# Initialize MongoDB client with proper codec options
try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[DB_NAME]
    collection = db.get_collection(
        COLLECTION_NAME,
        codec_options=CodecOptions(tz_aware=True)
    )
    print("Connected to MongoDB Atlas successfully!")
except Exception as e:
    print(f"Failed to connect to MongoDB Atlas: {e}")
    exit(1)

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker successfully!")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect to MQTT broker with result code {rc}")

def on_disconnect(client, userdata, flags, rc):
    print(f"Disconnected from MQTT broker with result code {rc}")
    while not client.is_connected():
        try:
            print("Attempting to reconnect...")
            client.reconnect()
            time.sleep(5)
        except Exception as e:
            print(f"Reconnection failed: {e}")
            time.sleep(5)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Received payload: {payload}")

        current_time = datetime.utcnow()
        processed_data = {
            'soil_moisture': int(payload.get('soil_moisture', 0)),
            'rain_value': int(payload.get('rain_value', 0)),
            'is_raining': bool(payload.get('is_raining', False)),
            'soil_pump': payload.get('soil_pump', False),
            'arduino_timestamp': int(payload.get('timestamp', 0)),
            'BSON UTC': current_time
        }

        print(f"Processed data: {processed_data}")
        result = collection.insert_one(processed_data)
        print(f"Data inserted with ID: {result.inserted_id}")
    except Exception as e:
        print(f"Error processing message: {e}")

# Start MQTT client in a separate thread
def start_mqtt_client():
    client = mqtt.Client(client_id="python_subscriber", clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    while True:
        try:
            print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            break
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            time.sleep(5)

    client.loop_forever()

# Flask API Endpoints
@app.route("/sensor_data", methods=["GET"])
def get_sensor_data():
    try:
        limit = int(request.args.get("limit", 10))  # Limit results
        data = list(collection.find().sort("_id", -1).limit(limit))
        return jsonify(json.loads(json_util.dumps(data))), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/sensor_data", methods=["POST"])
def add_sensor_data():
    try:
        sensor_data = request.json
        sensor_data["BSON UTC"] = datetime.utcnow()
        result = collection.insert_one(sensor_data)
        return jsonify({"message": "Data inserted", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def health_check():
    return jsonify({"message": "Flask API is running!"}), 200

# Main function
if __name__ == "__main__":
    # Start MQTT client in a separate thread
    mqtt_thread = Thread(target=start_mqtt_client, daemon=True)
    mqtt_thread.start()

    # Start Flask API
    app.run(host="0.0.0.0", port=5000, debug=True)
