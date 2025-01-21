from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime
import pytz

# MongoDB Atlas configuration
MONGO_URI = "mongodb+srv://kuzafri:kuzafri313@conms.i2dnl.mongodb.net/?retryWrites=true&w=majority&appName=conms"
DB_NAME = "SmartAgro"
COLLECTION_NAME = "sensor_data"

def fetch_data():
    """Fetch data from MongoDB and convert to DataFrame"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Fetch all documents
        cursor = collection.find({})
        data = list(cursor)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Convert BSON UTC to local time and extract hour
        df['hour'] = pd.to_datetime(df['BSON UTC']).dt.hour
        
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    finally:
        client.close()

def prepare_features(df):
    """Prepare features for the model"""
    # Select relevant features
    features = ['soil_moisture', 'rain_value', 'is_raining', 'hour']
    target = 'soil_pump'
    
    # Drop rows with missing values
    df = df.dropna(subset=features + [target])
    
    # Convert boolean to integer
    df['is_raining'] = df['is_raining'].astype(int)
    
    # Create a copy of the features DataFrame
    X = df[features].copy()
    y = df[target].astype(int)
    
    # Scale numerical features
    scaler = StandardScaler()
    numerical_features = ['soil_moisture', 'rain_value']
    X.loc[:, numerical_features] = scaler.fit_transform(X[numerical_features])
    
    # Save the scaler for future predictions
    joblib.dump(scaler, 'feature_scaler.joblib')
    
    return X, y

def train_model():
    """Train the Random Forest model"""
    # Fetch and prepare data
    df = fetch_data()
    if df is None:
        return None
    
    X, y = prepare_features(df)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y  # Added stratification
    )
    
    # Create and train the model with adjusted parameters
    model = RandomForestClassifier(
        n_estimators=200,  # Increased number of trees
        max_depth=5,       # Reduced max_depth to prevent overfitting
        min_samples_split=5,  # Added to prevent overfitting
        class_weight='balanced',  # Added to handle imbalanced classes
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    print("\nModel Performance:")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print("\nFeature Importance:")
    print(feature_importance)
    
    # Save the model
    model_filename = 'water_pump_model.joblib'
    joblib.dump(model, model_filename)
    print(f"\nModel saved as {model_filename}")
    
    return model

def predict_pump_status(model, soil_moisture, rain_value, is_raining, hour=None):
    """Predict whether to turn on the pump based on current conditions"""
    if hour is None:
        hour = datetime.now().hour
    
    try:
        # Load the scaler
        scaler = joblib.load('feature_scaler.joblib')
        
        # Create DataFrame with proper column names
        features = pd.DataFrame({
            'soil_moisture': [soil_moisture],
            'rain_value': [rain_value],
            'is_raining': [int(is_raining)],
            'hour': [hour]
        })
        
        # Scale only numerical features
        numerical_features = ['soil_moisture', 'rain_value']
        features[numerical_features] = scaler.transform(features[numerical_features])
        
        # Make prediction
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0]
        
        return bool(prediction), probability
    except Exception as e:
        print(f"Error in prediction: {e}")
        return None, None

if __name__ == "__main__":
    print("Training Random Forest model for water pump prediction...")
    model = train_model()
    
    if model:
        # Test with the provided real data point
        soil_moisture = 1798  # Real value from the data
        rain_value = 2174    # Real value from the data
        is_raining = False   # Real value from the data
        hour = 8            # From the timestamp provided
        
        should_pump, probability = predict_pump_status(model, soil_moisture, rain_value, is_raining, hour)
        print(f"\nPrediction for Real Data Point:")
        print(f"Soil Moisture: {soil_moisture}")
        print(f"Rain Value: {rain_value}")
        print(f"Is Raining: {is_raining}")
        print(f"Hour: {hour}")
        print(f"Should turn on pump: {should_pump}")
        print(f"Prediction probability: {probability}")
        
        # Also test with some different moisture levels
        test_moisture_levels = [500, 1000, 1500, 2000]
        print("\nTesting different moisture levels:")
        for moisture in test_moisture_levels:
            should_pump, probability = predict_pump_status(model, moisture, rain_value, is_raining, hour)
            print(f"\nSoil Moisture: {moisture}")
            print(f"Should turn on pump: {should_pump}")
            print(f"Prediction probability: {probability}") 