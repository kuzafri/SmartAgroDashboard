from flask import Flask, jsonify, request
from threading import Thread
import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
from datetime import datetime
from bson import CodecOptions, json_util
from flask_cors import CORS
import joblib
import time
import pandas as pd
from soil_moisture_model import train_model, predict_future_moisture

# MongoDB Atlas configuration
MONGO_URI = "mongodb+srv://kuzafri:kuzafri313@conms.i2dnl.mongodb.net/?retryWrites=true&w=majority&appName=conms"
DB_NAME = "SmartAgro"
COLLECTION_NAME = "sensor_data"

# MQTT configuration
MQTT_BROKER = "34.42.195.199"
MQTT_PORT = 1883
MQTT_TOPIC = "SmartAgro"
MQTT_CONTROL_TOPIC = "SmartAgro/control"  # New topic for control commands

# Flask application
app = Flask(__name__)
CORS(app)

# Load the trained model and scaler
try:
    model = joblib.load('water_pump_model.joblib')
    scaler = joblib.load('feature_scaler.joblib')
    print("Loaded ML model and scaler successfully!")
except Exception as e:
    print(f"Failed to load ML model or scaler: {e}")
    exit(1)

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

# MQTT client for publishing control commands
mqtt_publisher = mqtt.Client(client_id="python_publisher", clean_session=True)

def predict_pump_status(soil_moisture, rain_value, is_raining):
    try:
        current_hour = datetime.now().hour
        
        # Create features DataFrame
        features = pd.DataFrame({
            'soil_moisture': [soil_moisture],
            'rain_value': [rain_value],
            'is_raining': [int(is_raining)],
            'hour': [current_hour]
        })
        
        # Scale numerical features
        numerical_features = ['soil_moisture', 'rain_value']
        features[numerical_features] = scaler.transform(features[numerical_features])
        
        # Make prediction
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0]
        
        return bool(prediction), probability
    except Exception as e:
        print(f"Error in prediction: {e}")
        return None, None

def publish_pump_control(should_pump_on):
    try:
        control_message = {
            'command': 'pump',
            'state': should_pump_on,
            'timestamp': int(time.time())
        }
        mqtt_publisher.publish(MQTT_CONTROL_TOPIC, json.dumps(control_message))
        print(f"Published pump control command: {control_message}")
    except Exception as e:
        print(f"Error publishing pump control: {e}")

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

        # Extract sensor data
        soil_moisture = int(payload.get('soil_moisture', 0))
        rain_value = int(payload.get('rain_value', 0))
        is_raining = bool(payload.get('is_raining', False))
        
        # Get model prediction
        should_pump, probability = predict_pump_status(soil_moisture, rain_value, is_raining)
        
        if should_pump is not None:
            # Publish pump control command
            publish_pump_control(should_pump)
            
            # Store data with prediction
            current_time = datetime.utcnow()
            processed_data = {
                'soil_moisture': soil_moisture,
                'rain_value': rain_value,
                'is_raining': is_raining,
                'soil_pump': should_pump,
                'prediction_probability': probability.tolist(),
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

    # Connect publisher
    try:
        mqtt_publisher.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        mqtt_publisher.loop_start()
    except Exception as e:
        print(f"Failed to connect publisher to MQTT broker: {e}")

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

@app.route('/train_moisture_model', methods=['POST'])
def train_moisture_model():
    try:
        model = train_model()
        return jsonify({'message': 'Model trained successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/moisture_predictions', methods=['GET'])
def get_moisture_predictions():
    try:
        hours = request.args.get('hours', default=24, type=int)
        predictions = predict_future_moisture(hours)
        return jsonify(predictions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Start MQTT client in a separate thread
    mqtt_thread = Thread(target=start_mqtt_client, daemon=True)
    mqtt_thread.start()

    # Start Flask API
    app.run(host="0.0.0.0", port=5000, debug=True)
