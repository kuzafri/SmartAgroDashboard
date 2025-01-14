import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt

def train_and_evaluate(data_file, model_name="Model"):
    # Load data
    data = pd.read_csv(data_file)
    X = data[['moisture', 'temp']]
    y = data['pump']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Print results
    print(f"\n{model_name} Results:")
    print(classification_report(y_test, y_pred))
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    plt.scatter(X[y == 0]['moisture'], X[y == 0]['temp'], label='Pump OFF', alpha=0.6)
    plt.scatter(X[y == 1]['moisture'], X[y == 1]['temp'], label='Pump ON', alpha=0.6)
    plt.xlabel('Moisture Level')
    plt.ylabel('Temperature')
    plt.title(f'Pump Status - {model_name}')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    return model

# Train models on all datasets
model1 = train_and_evaluate('data.csv', "Original Dataset")
model2 = train_and_evaluate('data2.csv', "Dataset 2")
model3 = train_and_evaluate('data3.csv', "Dataset 3")

# Test prediction consistency
def test_consistency(models, moisture, temp):
    predictions = []
    confidences = []
    
    for model in models:
        pred = model.predict([[moisture, temp]])[0]
        conf = model.predict_proba([[moisture, temp]])[0][pred]
        predictions.append(pred)
        confidences.append(conf)
    
    return predictions, confidences

# Test some sample cases
test_cases = [
    (700, 25),  # High moisture
    (200, 25),  # Low moisture
    (500, 40)   # Medium moisture, high temp
]

print("\nModel Consistency Test:")
for moisture, temp in test_cases:
    preds, confs = test_consistency([model1, model2, model3], moisture, temp)
    print(f"\nMoisture: {moisture}, Temperature: {temp}")
    print(f"Predictions: {preds}")
    print(f"Confidences: {[f'{c:.2%}' for c in confs]}")