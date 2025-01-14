from flask import Flask, request, jsonify
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd
import numpy as np
import pickle
import os
from io import BytesIO
import base64

app = Flask(__name__)

UPLOAD_FOLDER = 'models'
ALLOWED_EXTENSIONS = {'pkl'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model = None
voting_clf = None
data = None
X_train = None
y_train = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/load_csv', methods=['POST'])
def load_csv():
    global data, X_train, y_train, model, voting_clf
    try:
        file_content = request.json['file_content']
        csv_file = BytesIO(base64.b64decode(file_content))
        data = pd.read_csv(csv_file)
        
        # Extract features (moisture and temp) and target (pump)
        X = data[['moisture', 'temp']].values
        y = data['pump'].values
        
        if X.shape[1] != 2:
            return jsonify({"error": "CSV data must have exactly 2 features (moisture and temperature)"}), 400
            
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Initialize and train the model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Initialize and train the voting classifier
        voting_clf = VotingClassifier(estimators=[('model1', model)], voting='soft')
        voting_clf.fit(X_train, y_train)
        
        # Calculate and return initial model performance
        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        return jsonify({
            "message": "CSV loaded and initial model trained successfully",
            "features": X.shape[1],
            "accuracy": report['accuracy'],
            "samples": len(X)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/predict', methods=['POST'])
def predict():
    global model
    try:
        data = request.json
        # Expect moisture and temperature as input
        moisture = data['moisture']
        temperature = data['temperature']
        
        sample = np.array([[moisture, temperature]])
        prediction = model.predict(sample)[0]
        probability = model.predict_proba(sample)[0].max()

        return jsonify({
            "prediction": int(prediction),  # 1 means pump should be activated, 0 means no pumping needed
            "probability": float(probability),
            "recommendation": "Activate pump" if prediction == 1 else "No pumping needed"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/improve_model', methods=['POST'])
def improve_model():
    global model, voting_clf, X_train, y_train
    try:
        data = request.json
        new_moisture = data.get('moisture')
        new_temperature = data.get('temperature')
        new_pump_decision = data.get('pump_decision')
        
        if None in (new_moisture, new_temperature, new_pump_decision):
            return jsonify({"error": "Missing required data"}), 400

        new_sample = np.array([[new_moisture, new_temperature]])
        new_label = np.array([new_pump_decision])

        # Update training data
        if X_train is None or y_train is None:
            X_train = new_sample
            y_train = new_label
        else:
            X_train = np.vstack((X_train, new_sample))
            y_train = np.append(y_train, new_label)

        # Retrain models with updated data
        model.fit(X_train, y_train)
        voting_clf = VotingClassifier(estimators=[('model1', model)], voting='soft')
        voting_clf.fit(X_train, y_train)

        # Make prediction with updated model
        prediction = model.predict(new_sample)[0]
        probability = model.predict_proba(new_sample)[0].max()

        return jsonify({
            "message": "Model successfully updated",
            "new_prediction": int(prediction),
            "probability": float(probability),
            "training_samples": len(X_train)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/save_model', methods=['POST'])
def save_model():
    global model
    try:
        model_name = request.json['model_name']
        models_dir = os.path.join(os.getcwd(), 'models')

        if not os.path.exists(models_dir):
            os.makedirs(models_dir)

        model_path = os.path.join(models_dir, f"{model_name}.pkl")
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)

        return jsonify({"message": "Model saved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/load_model', methods=['POST'])
def load_model():
    global model, voting_clf
    try:
        model_name = request.json['model_name']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], model_name)

        with open(file_path, 'rb') as f:
            model = pickle.load(f)

        if isinstance(model, RandomForestClassifier):
            voting_clf = VotingClassifier(estimators=[('model1', model)], voting='soft')
            return jsonify({"message": "Model loaded successfully"})
        else:
            return jsonify({"error": "Unsupported model type. Expected RandomForestClassifier."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)