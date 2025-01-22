#include <WiFi.h>
#include <PubSubClient.h>
#include <TimeLib.h>  // Add time management


// WiFi credentials
const char* ssid = "cslab";
const char* password = "aksesg31";

// MQTT Broker settings
const char* mqtt_server = "34.71.125.87";
const int mqtt_port = 1883;
const char* mqtt_topic = "SmartAgro";

// Pin Definitions
const int soilMoisturePin = 34;    // ADC pin GPIO34
const int rainAnalogPin = 35;      // Changed to analog pin for rain sensor
const int soilPumpPin = 32;        // GPIO32 for soil moisture pump

// Enhanced Thresholds and Settings
struct ThresholdSettings {
    int morningMoisture;    // 6AM-10AM
    int daytimeMoisture;    // 10AM-6PM
    int eveningMoisture;    // 6PM-10PM
    int nighttimeMoisture;  // 10PM-6AM
} thresholds = {2100, 2300, 2200, 2400};

// Safety Settings
const unsigned long MAX_PUMP_RUNTIME = 300000;  // 5 minutes
const unsigned long MIN_PUMP_INTERVAL = 3600000;  // 1 hour
unsigned long lastPumpStart = 0;
unsigned long lastPumpStop = 0;

const int MOISTURE_THRESHOLD = 2300;  // Low moisture threshold
const int RAIN_THRESHOLD = 2000;    // Added rain threshold - adjust this value based on testing
bool soilPumpStatus = false;

// Zone Management
struct Zone {
    int moisturePin;
    int moistureReading;
    bool needsWater;
    unsigned long lastWatered;
} zones[3];

void setupZones() {
    for(int i = 0; i < 3; i++) {
        zones[i].moisturePin = soilMoisturePin;
        zones[i].moistureReading = 0;
        zones[i].needsWater = false;
        zones[i].lastWatered = 0;
    }
}

int getCurrentThreshold() {
    int hour = (millis() / 3600000) % 24;  // Simplified time calculation
    
    if(hour >= 6 && hour < 10) return thresholds.morningMoisture;
    if(hour >= 10 && hour < 18) return thresholds.daytimeMoisture;
    if(hour >= 18 && hour < 22) return thresholds.eveningMoisture;
    return thresholds.nighttimeMoisture;
}

bool isSafeToActivatePump() {
    unsigned long currentTime = millis();
    
    // Check if minimum interval has passed since last pump operation
    if(currentTime - lastPumpStop < MIN_PUMP_INTERVAL) return false;
    
    // Check if pump has been running too long
    if(soilPumpStatus && (currentTime - lastPumpStart > MAX_PUMP_RUNTIME)) {
        return false;
    }
    
    return true;
}

void updateZones() {
    int currentThreshold = getCurrentThreshold();
    for(int i = 0; i < 3; i++) {
        zones[i].moistureReading = analogRead(zones[i].moisturePin);
        zones[i].needsWater = (zones[i].moistureReading < currentThreshold);
    }
}

bool shouldActivatePump() {
    int rainValue = analogRead(rainAnalogPin);
    bool isRaining = (rainValue < RAIN_THRESHOLD);
    
    if(isRaining) return false;
    
    // Check if any zone needs water
    bool anyZoneNeedsWater = false;
    for(int i = 0; i < 3; i++) {
        if(zones[i].needsWater) {
            anyZoneNeedsWater = true;
            break;
        }
    }
    
    return anyZoneNeedsWater && isSafeToActivatePump();
}

void controlPump() {
    if(shouldActivatePump() && !soilPumpStatus) {
        digitalWrite(soilPumpPin, HIGH);
        soilPumpStatus = true;
        lastPumpStart = millis();
        Serial.println("Pump activated");
    } 
    else if((!shouldActivatePump() || !isSafeToActivatePump()) && soilPumpStatus) {
        digitalWrite(soilPumpPin, LOW);
        soilPumpStatus = false;
        lastPumpStop = millis();
        Serial.println("Pump deactivated");
    }
}

// Variables
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  // Configure pins
  pinMode(soilPumpPin, OUTPUT);
  digitalWrite(soilPumpPin, LOW);  // Ensure pump starts OFF
  soilPumpStatus = false;  // Initialize pump status to OFF
  
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  
  // Test sensor readings
  Serial.println("Initial sensor readings:");
  Serial.print("Soil moisture: ");
  Serial.println(analogRead(soilMoisturePin));
  Serial.print("Rain analog value: ");
  Serial.println(analogRead(rainAnalogPin));
  Serial.print("Soil Pump Status: ");
  Serial.println(soilPumpStatus ? "ON" : "OFF");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 1000) {  // Send every second
    lastMsg = now;

    updateZones();
    controlPump();
    
    // Read sensors
    int soilMoisture = analogRead(soilMoisturePin);
    int rainValue = analogRead(rainAnalogPin);
    bool isRaining = (rainValue < RAIN_THRESHOLD);
    
    // Debug prints
    Serial.println("\nSensor Readings:");
    Serial.print("Soil Moisture: ");
    Serial.println(soilMoisture);
    Serial.print("Rain Value: ");
    Serial.println(rainValue);
    Serial.print("Is Raining: ");
    Serial.println(isRaining);
    Serial.print("Soil Pump Status: ");
    Serial.println(soilPumpStatus ? "ON" : "OFF");

        // Create enhanced JSON string with all zone data
        String jsonString = "{\"zones\":[";
        for(int i = 0; i < 3; i++) {
            if(i > 0) jsonString += ",";
            jsonString += "{\"moisture\":" + String(zones[i].moistureReading) + 
                         ",\"needs_water\":" + String(zones[i].needsWater ? "true" : "false") + "}";
        }
        jsonString += "],\"rain_value\":" + String(analogRead(rainAnalogPin)) + 
                     ",\"soil_pump\":" + String(soilPumpStatus ? "true" : "false") + 
                     ",\"timestamp\":" + String(now) + "}";
        
        client.publish(mqtt_topic, jsonString.c_str());
  }
}