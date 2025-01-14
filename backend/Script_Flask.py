from flask import Flask, request, jsonify
from pymongo import MongoClient
import json
from datetime import datetime
from bson import CodecOptions
import paho.mqtt.client as mqtt
import threading
import time

app = Flask(__name__)

# MongoDB Atlas configuration
MONGO_URI = "mongodb+srv://kuzafri:kuzafri313@conms.i2dnl.mongodb.net/?retryWrites=true&w=majority&appName=conms"
DB_NAME = "SmartAgro"
COLLECTION_NAME = "sensor_data"

# MQTT configuration
MQTT_BROKER = "34.173.50.167"
MQTT_PORT = 1883
MQTT_TOPIC = "SmartAgro"

# Initialize MongoDB client
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

# MQTT client initialization
mqtt_client = mqtt.Client(client_id="flask_subscriber", clean_session=True)

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
            'rain_analog': int(payload.get('rain_analog', 0)),
            'rain_digital': bool(payload.get('rain_digital', False)),
            'soil_pump': payload.get('soil_pump', False),
            'rain_pump': payload.get('rain_pump', False),
            'arduino_timestamp': int(payload.get('timestamp', 0)),
            'BSON UTC': current_time
        }

        print(f"Processed data before insert: {processed_data}")

        result = collection.insert_one(processed_data)
        print(f"Data inserted with ID: {result.inserted_id}")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Raw payload: {msg.payload.decode()}")
    except Exception as e:
        print(f"Error processing message: {e}")

# Set MQTT client callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.on_disconnect = on_disconnect

# Flask route to start the MQTT client
@app.route("/start", methods=["POST"])
def start_mqtt():
    def mqtt_loop():
        connected = False
        while not connected:
            try:
                print(f"Attempting to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
                mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
                connected = True
            except Exception as e:
                print(f"Failed to connect to MQTT broker: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)

        mqtt_client.loop_forever()

    thread = threading.Thread(target=mqtt_loop)
    thread.daemon = True
    thread.start()

    return jsonify({"message": "MQTT client started."}), 200

# Flask route to retrieve data from MongoDB
@app.route("/data", methods=["GET"])
def get_data():
    try:
        data = list(collection.find())
        for doc in data:
            doc["_id"] = str(doc["_id"])
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask route to insert data manually
@app.route("/insert", methods=["POST"])
def insert_data():
    try:
        payload = request.json
        current_time = datetime.utcnow()
        payload['BSON UTC'] = current_time
        result = collection.insert_one(payload)
        return jsonify({"message": "Data inserted.", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
