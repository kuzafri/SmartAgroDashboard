from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import random
from sklearn.preprocessing import MinMaxScaler

load_dotenv()

def get_mongo_connection():
    try:
        MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        print(f"Attempting to connect to MongoDB...")
        client = MongoClient(MONGO_URI)
        # Test the connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        raise

def generate_synthetic_data(n_samples=1000):
    """Generate synthetic soil moisture data with realistic patterns."""
    np.random.seed(42)
    
    # Create timestamp range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # Increased to 90 days for more seasonal patterns
    timestamps = pd.date_range(start=start_date, end=end_date, periods=n_samples)
    
    # Base moisture patterns with more realistic variation
    base_moisture = np.random.normal(loc=35, scale=3, size=n_samples)  # Reduced variance for more stability
    
    # Enhanced time-of-day pattern
    hour_effect = -2 * np.sin(timestamps.hour * 2 * np.pi / 24) * \
                 (1 + 0.3 * np.sin(timestamps.dayofyear * 2 * np.pi / 365))  # Seasonal variation in daily pattern
    
    # Enhanced weekly pattern
    day_effect = np.sin(timestamps.dayofweek * 2 * np.pi / 7) * 1.5
    
    # Seasonal pattern
    seasonal_effect = 5 * np.sin(timestamps.dayofyear * 2 * np.pi / 365)
    
    # Temperature effect (simulated)
    temp_effect = 2 * np.sin(timestamps.hour * 2 * np.pi / 24 + np.pi) * \
                 (1 + 0.5 * np.sin(timestamps.dayofyear * 2 * np.pi / 365))
    
    # Combine all effects
    soil_moisture = base_moisture + hour_effect + day_effect + seasonal_effect - temp_effect
    
    # Convert to numpy array to ensure we can modify it
    soil_moisture = np.array(soil_moisture)
    
    # Add some random events (like rainfall)
    rain_events = np.random.random(n_samples) > 0.95  # 5% chance of rain
    rain_intensity = np.random.exponential(scale=5, size=n_samples)  # More realistic rain distribution
    soil_moisture = soil_moisture + (rain_events * rain_intensity)
    
    # Add some dry spells (periods of gradual moisture decrease)
    dry_spell_starts = np.random.random(n_samples) > 0.97
    dry_spell_length = 72  # 3 days
    
    # Create a dry spell effect array
    dry_spell_effect = np.zeros(n_samples)
    for i in range(n_samples):
        if dry_spell_starts[i] and i + dry_spell_length < n_samples:
            decay = np.linspace(0, -10, dry_spell_length)
            dry_spell_effect[i:i+dry_spell_length] += decay
    
    # Apply dry spell effect
    soil_moisture += dry_spell_effect
    
    # Ensure values are realistic (between 0 and 100)
    soil_moisture = np.clip(soil_moisture, 0, 100)
    
    # Create DataFrame
    df = pd.DataFrame({
        'BSON UTC': [{'$date': ts.isoformat()} for ts in timestamps],
        'soil_moisture': soil_moisture
    })
    
    return df

def prepare_data(use_synthetic=False, n_synthetic_samples=1000):
    if use_synthetic:
        df = generate_synthetic_data(n_synthetic_samples)
    else:
        client = get_mongo_connection()
        db = client['SmartAgro']
        collection = db['sensor_data']
        
        # Get sensor data
        data = list(collection.find({}, {'soil_moisture': 1, 'BSON UTC': 1, '_id': 0}))
        df = pd.DataFrame(data)
    
    # Convert BSON UTC to datetime
    df['timestamp'] = pd.to_datetime(df['BSON UTC'].apply(lambda x: x['$date'] if isinstance(x, dict) else x))
    
    # Enhanced time-based features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    df['day_of_month'] = df['timestamp'].dt.day
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Time of day categories
    df['time_of_day'] = pd.cut(df['hour'], 
                              bins=[-1, 6, 12, 18, 23], 
                              labels=['night', 'morning', 'afternoon', 'evening'])
    df = pd.get_dummies(df, columns=['time_of_day'])
    
    # Create more sophisticated lag features
    for i in range(1, 7):
        df[f'moisture_lag{i}'] = df['soil_moisture'].shift(i)
    
    # Add rolling mean and std features
    df['moisture_rolling_mean_3h'] = df['soil_moisture'].rolling(window=3).mean()
    df['moisture_rolling_mean_6h'] = df['soil_moisture'].rolling(window=6).mean()
    df['moisture_rolling_std_3h'] = df['soil_moisture'].rolling(window=3).std()
    df['moisture_rolling_std_6h'] = df['soil_moisture'].rolling(window=6).std()
    
    # Add rate of change features
    df['moisture_change_1h'] = df['soil_moisture'] - df['moisture_lag1']
    df['moisture_change_3h'] = df['soil_moisture'] - df['moisture_lag3']
    
    # Drop rows with NaN values
    df = df.dropna()
    
    # Prepare features and target
    feature_columns = ['hour', 'day_of_week', 'month', 'day_of_month', 'is_weekend'] + \
                     [col for col in df.columns if col.startswith('time_of_day_')] + \
                     [f'moisture_lag{i}' for i in range(1, 7)] + \
                     ['moisture_rolling_mean_3h', 'moisture_rolling_mean_6h',
                      'moisture_rolling_std_3h', 'moisture_rolling_std_6h',
                      'moisture_change_1h', 'moisture_change_3h']
    
    X = df[feature_columns]
    y = df['soil_moisture']
    
    return X, y

def train_model(use_synthetic=True, n_synthetic_samples=20000):  # Increased samples
    """Train the model with option to use synthetic data"""
    X, y = prepare_data(use_synthetic=use_synthetic, n_synthetic_samples=n_synthetic_samples)
    
    # Split the data with stratification
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create and train an improved Random Forest model with better parameters
    model = RandomForestRegressor(
        n_estimators=500,      # Increased from 200
        max_depth=20,          # Increased from 15
        min_samples_split=4,   # Decreased from 5 for more granular splits
        min_samples_leaf=1,    # Decreased from 2 for more precise predictions
        max_features='sqrt',   # Auto feature selection
        bootstrap=True,        # Enable bootstrapping
        n_jobs=-1,
        random_state=42
    )
    
    # Train the model with cross-validation
    from sklearn.model_selection import cross_val_score
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
    print("\nCross-validation scores:", cv_scores)
    print("Average CV score:", cv_scores.mean())
    
    # Train final model
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    mae = np.mean(np.abs(y_test - y_pred))
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    
    # Calculate feature importance
    feature_importance = dict(zip(X.columns, model.feature_importances_))
    
    print("\nModel Performance Metrics:")
    print(f"Mean Squared Error (MSE): {mse:.2f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
    print(f"Mean Absolute Error (MAE): {mae:.2f}")
    print(f"Mean Absolute Percentage Error (MAPE): {mape:.2f}%")
    print(f"R² Score: {r2:.4f}")
    print("\nTop 10 Most Important Features:")
    for feature, importance in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{feature}: {importance:.4f}")
    
    # Save the model
    joblib.dump(model, 'soil_moisture_rf_model.joblib')
    
    return model

def predict_future_moisture(hours_ahead=24):
    client = get_mongo_connection()
    db = client['SmartAgro']
    collection = db['sensor_data']
    
    # Load the model
    model = joblib.load('soil_moisture_rf_model.joblib')
    
    # Get recent data
    recent_data = list(collection.find({}).sort([('BSON UTC', -1)]).limit(3))
    recent_moisture = [d['soil_moisture'] for d in reversed(recent_data)]
    
    predictions = []
    current_time = datetime.now()
    
    for i in range(hours_ahead):
        future_time = current_time + timedelta(hours=i)
        
        # Create feature vector
        features = np.array([[
            future_time.hour,
            future_time.weekday(),
            recent_moisture[-1],
            recent_moisture[-2],
            recent_moisture[-3]
        ]])
        
        # Make prediction
        pred = model.predict(features)[0]
        predictions.append({
            'timestamp': future_time.strftime('%Y-%m-%d %H:%M:%S'),
            'predicted_moisture': pred
        })
        
        # Update recent moisture values for next prediction
        recent_moisture = recent_moisture[1:] + [pred]
    
    return predictions

if __name__ == "__main__":
    # Train with 20000 synthetic samples
    model = train_model(use_synthetic=True, n_synthetic_samples=20000) 