import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt

# Load and prepare the data
def load_data(csv_file):
    data = pd.read_csv(csv_file)
    
    # Select features (moisture and temp) and target (pump)
    X = data[['moisture', 'temp']]
    y = data['pump']
    
    return X, y

# Load the data
X, y = load_data('backend/data.csv')

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)

# Print model performance
print("------------------- Model Performance --------------------")
print(classification_report(y_test, y_pred))

# Feature importance analysis
feature_importance = pd.DataFrame({
    'feature': ['Moisture', 'Temperature'],
    'importance': model.feature_importances_
})
print("\nFeature Importance:")
print(feature_importance.sort_values(by='importance', ascending=False))

# Function to predict pump status for new data
def predict_pump_status(moisture, temp):
    new_data = np.array([[moisture, temp]])
    prediction = model.predict(new_data)[0]
    probability = model.predict_proba(new_data)[0]
    
    confidence = probability[1] if prediction == 1 else probability[0]
    return prediction, confidence

# Example prediction
print("\nExample Predictions:")
test_cases = [
    (700, 25),  # High moisture
    (200, 25),  # Low moisture
    (500, 40)   # Medium moisture, high temp
]

for moisture, temp in test_cases:
    prediction, confidence = predict_pump_status(moisture, temp)
    print(f"Moisture: {moisture}, Temperature: {temp}")
    print(f"Predicted Pump Status: {'ON' if prediction == 1 else 'OFF'}")
    print(f"Confidence: {confidence:.2%}\n")

# Visualization of decision boundaries
plt.figure(figsize=(10, 6))
plt.scatter(X[y == 0]['moisture'], X[y == 0]['temp'], label='Pump OFF', alpha=0.6)
plt.scatter(X[y == 1]['moisture'], X[y == 1]['temp'], label='Pump ON', alpha=0.6)
plt.xlabel('Moisture Level')
plt.ylabel('Temperature')
plt.title('Pump Status Based on Moisture and Temperature')
plt.legend()
plt.grid(True)
plt.show()