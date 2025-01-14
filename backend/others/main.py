#!/tools/activepython/latest/bin/python3

from flask import Flask, request, jsonify, redirect, url_for, send_from_directory
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from io import StringIO
import pandas as pd
import numpy as np
import pickle
import os
import requests
import base64
from io import BytesIO
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'models'
ALLOWED_EXTENSIONS = {'pkl'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model = []
voting_clf = None
data = None
X_train = None
y_train = None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return redirect(url_for('start_php_server'))

@app.route('/index.php')
def start_php_server():
    return send_from_directory(os.getcwd(), 'index.php')

@app.route('/improve_model.php')
def improve_model_page():
    return send_from_directory(os.getcwd(), 'improve_model.php')

@app.route('/list_models', methods=['GET'])
def list_models():
    models_dir = os.path.join(os.getcwd(), 'models')
    model_files = [f for f in os.listdir(models_dir) if f.endswith('.pkl')]
    return jsonify({"models": model_files})

@app.route('/load_model', methods=['POST'])
def load_model():
    global model, voting_clf
    try:
        model_name = request.json['model_name']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], model_name)

        with open(file_path, 'rb') as f:
            model = pickle.load(f)

        print(f"Loaded model type: {type(model)}")
        if isinstance(model, RandomForestClassifier):
            voting_clf = VotingClassifier(estimators=[('model1', model)], voting='soft')
        else:
            return jsonify({"error": f"Unsupported model type: {type(model)}. Expected RandomForestClassifier."}), 400

        return jsonify({"message": "Model loaded successfully"})

    except Exception as e:
        print(f"Error in load_model: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/save_improved_model', methods=['POST'])
def save_improved_model():
    global voting_clf
    try:
        model_name = request.json['model_name']
        with open(model_name + '_improved.pkl', 'wb') as f:
            pickle.dump(voting_clf, f)
        return jsonify({"message": "Improved model saved successfully!"})
    except Exception as e:
        return str(e), 400

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Test successful"})

@app.route('/load_csv', methods=['POST'])
def load_csv():
    global data, X_train, y_train, model, voting_clf
    try:
        file_content = request.json['file_content']
        csv_file = BytesIO(base64.b64decode(file_content))
        data = pd.read_csv(csv_file)

        data = data.drop('bank_number', axis=1)
        X = data.iloc[:, :-1].values
        y = data.iloc[:, -1].values
        if X.shape[1] != 8:
            return jsonify({"error": "CSV data must have exactly 8 features"}), 400
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        voting_clf = VotingClassifier(estimators=[('model1', model)], voting='soft')
        voting_clf.fit(X_train, y_train)
        return jsonify({"message": "CSV loaded and initial model trained successfully", "features": X.shape[1]})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/train', methods=['POST'])
def train_model():
    global model, voting_clf, X_train, y_train
    try:
        data = request.json
        new_data = data.get('new_data', [])
        filled_indices = data.get('filled_indices', [])
        all_inputs = data.get('all_inputs', [])

        print("All inputs (including randomized):")
        print("BANK\tHVCORNER\tIO\tCAP\tPOWERH\tPOWER\tGROUND\tPROBE\tFUSE")
        print("\t".join(map(str, all_inputs)))

        if new_data:
            if len(new_data) != 9:
                return jsonify({"error": "Input data must have exactly 9 values (8 features + 1 label)"}), 400

            new_sample = np.array(new_data[:-1]).reshape(1, -1)
            new_label = np.array([new_data[-1]])

            if filled_indices:
                filled_indices = [i for i in filled_indices if i < 8]
                new_sample_filled = new_sample[:, filled_indices]

                if X_train is None or y_train is None:
                    X_train = new_sample_filled
                    y_train = new_label
                else:
                    X_train = np.vstack((X_train[:, filled_indices], new_sample_filled))
                    y_train = np.hstack((y_train, new_label))

                subset_model = RandomForestClassifier(n_estimators=100, random_state=42)
                subset_model.fit(X_train, y_train)

                model.estimators_ = subset_model.estimators_

                voting_clf = VotingClassifier(estimators=[('model1', model)], voting='soft')
                voting_clf.fit(X_train, y_train)

                prediction = subset_model.predict(new_sample_filled)[0]
            else:
                prediction = None

            return jsonify({
                "prediction": int(prediction) if prediction is not None else None,
            })
        else:
            return jsonify({"error": "No new data provided"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/improve_model', methods=['POST'])
def improve_model():
    global model, voting_clf, X_train, y_train
    try:
        data = request.json
        new_data = data.get('new_data', [])
        filled_indices = data.get('filled_indices', [])
        all_inputs = data.get('all_inputs', [])

        print("All inputs (including randomized):")
        print("BANK\tHVCORNER\tIO\tCAP\tPOWERH\tPOWER\tGROUND\tPROBE\tFUSE")
        print("\t".join(map(str, all_inputs)))

        if len(new_data) != 9:
            return jsonify({"error": "Input data must have exactly 9 values (8 features + 1 label)"}), 400

        new_sample = np.array(new_data[:-1]).reshape(1, -1)
        new_label = np.array([new_data[-1]])

        if filled_indices:
            filled_indices = [i for i in filled_indices if i < 8]
            new_sample_filled = new_sample[:, filled_indices]

            if X_train is None or y_train is None:
                X_train = new_sample_filled
                y_train = new_label
            else:
                X_train = np.vstack((X_train[:, filled_indices], new_sample_filled))
                y_train = np.hstack((y_train, new_label))

            subset_model = RandomForestClassifier(n_estimators=100, random_state=42)
            subset_model.fit(X_train, y_train)

            model.estimators_ = subset_model.estimators_

            voting_clf = VotingClassifier(estimators=[('model1', model)], voting='soft')
            voting_clf.fit(X_train, y_train)

            prediction = subset_model.predict(new_sample_filled)[0]
        else:
            prediction = None

        return jsonify({
            "prediction": int(prediction) if prediction is not None else None,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/predict', methods=['POST'])
def predict():
    global model
    try:
        data = request.json
        sample = np.array(data['sample']).reshape(1, -1)
        prediction = model.predict(sample)[0]
        probability = model.predict_proba(sample)[0].max()

        return jsonify({
            "prediction": int(prediction),
            "probability": float(probability)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/save_model', methods=['POST'])
def save_model():
    global model, voting_clf
    try:
        model_name = request.json['model_name']
        models_dir = os.patha.join(os.getcwd(), 'models')

        if not os.path.exists(models_dir):
            os.makedirs(models_dir)

        rf_path = os.path.join(models_dir, f"{model_name}.pkl")
        # voting_path = os.path.join(models_dir, f"{model_name}_voting.pkl")

        with open(rf_path, 'wb') as f:
            pickle.dump(model, f)

        # with open(voting_path, 'wb') as f:
        #     pickle.dump(voting_clf, f)

        return jsonify({"message": "Model saved successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
