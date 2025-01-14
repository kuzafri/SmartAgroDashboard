import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
from datetime import datetime
import time
from bson import CodecOptions

# MongoDB Atlas configuration
MONGO_URI = "mongodb+srv://kuzafri:kuzafri313@conms.i2dnl.mongodb.net/?retryWrites=true&w=majority&appName=conms"
DB_NAME = "SmartAgro"
COLLECTION_NAME = "sensor_data"

# MQTT configuration
MQTT_BROKER = "34.173.50.167"
MQTT_PORT = 1883
MQTT_TOPIC = "SmartAgro"

# Initialize MongoDB client with proper codec options
try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[DB_NAME]
    # Set codec options to handle datetime
    collection = db.get_collection(
        COLLECTION_NAME,
        codec_options=CodecOptions(tz_aware=True)
    )
    print("Connected to MongoDB Atlas successfully!")
except Exception as e:
    print(f"Failed to connect to MongoDB Atlas: {e}")
    exit(1)

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
        # Parse the JSON payload
        payload = json.loads(msg.payload.decode())
        print(f"Received payload: {payload}")
        
        # Create the document with the required BSON UTC datetime
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
        
        # Insert into MongoDB Atlas
        result = collection.insert_one(processed_data)
        print(f"Data inserted with ID: {result.inserted_id}")
        
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Raw payload: {msg.payload.decode()}")
    except Exception as e:
        print(f"Error processing message: {e}")
        print(f"Full error details: {str(e)}")

def main():
    # Create MQTT client with clean session
    client = mqtt.Client(client_id="python_subscriber", clean_session=True)
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    # Connect to MQTT broker with retry mechanism
    connected = False
    while not connected:
        try:
            print(f"Attempting to connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            connected = True
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

    # Start the loop
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nDisconnecting from MQTT broker and MongoDB...")
        client.disconnect()
        mongo_client.close()
        print("Disconnected successfully")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()