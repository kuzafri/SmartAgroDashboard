from soil_moisture_model import train_model

if __name__ == "__main__":
    print("Training soil moisture model...")
    # Train with synthetic data since we might not have enough real data yet
    model = train_model(use_synthetic=True, n_synthetic_samples=20000)
    print("Model training completed and saved as soil_moisture_rf_model.joblib") 