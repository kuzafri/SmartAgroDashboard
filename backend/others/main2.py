#!/tools/activepython/latest/bin/python3

import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier,VotingClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.utils.validation import check_is_fitted

csv_files = {
    
    'model1': 'dummy2.csv',
    'model2': 'test2.csv',
    'model3': 'test3.csv'
}

def load_data(csv_file):
    data = pd.read_csv(csv_file)
    df = pd.DataFrame(data)

    df = df.drop(columns=['bank_number']) 
    X = df.drop(columns=['LABEL'])
    y = df['LABEL']

    X = X.values
    y = y.values

    return X, y

def feature_names():
    feature_names = X.columns.tolist()
    return feature_names

X_model1, y_model1 = load_data(csv_files['model1'])
X_model2, y_model2 = load_data(csv_files['model2'])
X_model3, y_model3 = load_data(csv_files['model3'])

_, X_test_model1, _, y_test_model1 = train_test_split(X_model1, y_model1, test_size = 0.4, random_state = 42)
_, X_test_model2, _, y_test_model2 = train_test_split(X_model2, y_model2, test_size = 0.4, random_state = 42)
_, X_test_model3, _, y_test_model3 = train_test_split(X_model3, y_model3, test_size = 0.4, random_state = 42)

with open('model1.pkl', 'rb') as f:
    model1 = pickle.load(f)

with open('model2.pkl', 'rb') as f:
    model2 = pickle.load(f)

with open('model3.pkl', 'rb') as f:
    model3 = pickle.load(f)

with open('voting_clf.pkl', 'rb') as f:
    voting_clf = pickle.load(f)

check_is_fitted(voting_clf, "estimators_")

X_test_combined = np.vstack((X_test_model1, X_test_model2, X_test_model3))
y_test_combined = np.hstack((y_test_model1, y_test_model2, y_test_model3))
y_pred_voting_combined = voting_clf.predict(X_test_combined)


# Fit the voting classifier
# voting_clf.fit(X_test_combined, y_test_combined)


print("-------------------Voting Classifier (Combined Model)--------------------")
print(classification_report(y_test_combined, y_pred_voting_combined, zero_division=0))

new_samples = [[0,25,0,0,8,5,0,0],[0,28,0,0,8,8,0,0],[0,29,0,0,8,7,0,0],[0,29,0,0,9,8,0,0],[0,35,0,0,10,10,0,0],[1,10,1,1,0,1,0,0],[1,6,1,1,0,1,0,0],[1,5,1,1,0,1,0,0],[1,9,1,1,0,1,0,0],[0,20,0,0,9,4,0,0],[1,8,1,1,0,1,0,0],[1,4,1,1,0,1,0,0],[0,0,0,0,14,17,0,1],{0,0,0,0,443,343,0,0],[0,66,0,0,71,52,0,0],[0,0,0,0,36,42,0,0],[0,21,0,0,19,13,0,0],[0,21,0,0,19,13,0,0],[0,0,0,0,20,14,0,0],[1,0,0,0,1,1,0,0],[1,0,0,0,1,1,0,0],[1,8,1,1,0,1,0,0],[1,8,1,1,0,1,0,0],[0,0,0,0,3,4,0,0],[1,0,0,0,1,1,0,0],[1,8,1,1,0,1,0,0],[1,6,1,1,0,1,0,0],[1,8,1,1,0,1,0,0],[1,0,0,0,1,1,0,0],[1,8,1,1,0,1,0,0],[1,0,0,0,1,1,0,0],[0,20,0,0,9,7,0,0]]

results = []

for sample in new_samples:
    predicted_class1 = model1.predict([sample])[0]
    predicted_class2 = model2.predict([sample])[0]
    predicted_class3 = model3.predict([sample])[0]

    confidence1 = model1.predict_proba([sample])[0].max()
    confidence2 = model2.predict_proba([sample])[0].max()
    confidence3 = model3.predict_proba([sample])[0].max()

    sample_result = [
        [predicted_class1, predicted_class2, predicted_class3],
        [f"{confidence1 * 100:.2f}%", f"{confidence2 * 100:.2f}%", f"{confidence3 * 100:.2f}%"]
    ]
    results.append(sample_result)

count = 0
for result in results:
    print(f"Predicted: {result[0]}, Confidence: {result[1]}")
    count += 1
    if count % 5 == 0:
        print() 

if count % 5 != 0:
    print()