import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.ensemble import VotingClassifier

csv_files = {
    'model1': 'test.csv',
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

# Split data into train and test sets for each model
X_train_model1, X_test_model1, y_train_model1, y_test_model1 = train_test_split(X_model1, y_model1, test_size=0.4, random_state=42)
X_train_model2, X_test_model2, y_train_model2, y_test_model2 = train_test_split(X_model2, y_model2, test_size=0.4, random_state=42)
X_train_model3, X_test_model3, y_train_model3, y_test_model3 = train_test_split(X_model3, y_model3, test_size=0.4, random_state=42)

# Train each RandomForestClassifier model separately
model1 = RandomForestClassifier(n_estimators=100, random_state=42)
model1.fit(X_train_model1, y_train_model1)

model2 = RandomForestClassifier(n_estimators=100, random_state=42)
model2.fit(X_train_model2, y_train_model2 )

model3 = RandomForestClassifier(n_estimators=100, random_state=42)
model3.fit(X_train_model3, y_train_model3 )

y_pred1 = model1.predict(X_test_model1)
y_pred_proba1 = model1.predict_proba(X_test_model1)

y_pred2 = model2.predict(X_test_model2)
y_pred_proba2 = model2.predict_proba(X_test_model2)

y_pred3 = model3.predict(X_test_model3)
y_pred_proba3 = model3.predict_proba(X_test_model3)

voting_clf = VotingClassifier(estimators=[
    ('model1', model1),
    ('model2', model2),
    ('model3', model3)
], voting='soft')

X_train_combined = np.vstack((X_train_model1, X_train_model2, X_train_model3))
y_train_combined = np.hstack((y_train_model1, y_train_model2, y_train_model3))

voting_clf.fit(X_train_combined, y_train_combined)

X_test_combined = np.vstack((X_test_model1, X_test_model2, X_test_model3))
y_test_combined = np.hstack((y_test_model1, y_test_model2, y_test_model3))
y_pred_voting_combined = voting_clf.predict(X_test_combined)

print("-------------------Voting Classifier (Combined Model)--------------------")
print(classification_report(y_test_combined, y_pred_voting_combined, zero_division=0))

#new_sample = [[1,1,3,4,0,1,0,0]]
new_sample = [[1,12,730,6,0,1,0,0],[1,12,730,6,0,1,0,0]]

proba1 = model1.predict_proba(new_sample)
proba2 = model2.predict_proba(new_sample)
proba3 = model3.predict_proba(new_sample)
voting_proba = voting_clf.predict_proba(new_sample)

predicted_class = voting_clf.predict(new_sample)[0]
predicted_class1 = model1.predict(new_sample)[0]
predicted_class2 = model2.predict(new_sample)[0]
predicted_class3 = model3.predict(new_sample)[0]

confidence1 = proba1[0][predicted_class]
confidence2 = proba2[0][predicted_class]
confidence3 = proba3[0][predicted_class]

print("Confidence levels for the new input from each model:")
print(f"Model 1: {confidence1 * 100:.2f}, [{predicted_class1}]")
print(f"Model 2: {confidence2 * 100:.2f}, [{predicted_class2}]")
print(f"Model 3: {confidence3 * 100:.2f}, [{predicted_class3}]")

# print(f"Voting Classifier: {voting_proba}")

# print(f"Voting Classifier: {voting_proba}")

combined_proba = np.mean([proba1, proba2, proba3], axis=0)
max_vote_index = np.argmax(combined_proba)
max_vote_confidence = combined_proba[0][max_vote_index]

print(f"\nVoting result: Class {max_vote_index} with confidence level {max_vote_confidence}")

print("-------------------Model 1--------------------")
print(classification_report(y_test_model1, y_pred1, zero_division=0))
print("-------------------Model 2--------------------")
print(classification_report(y_test_model2, y_pred2, zero_division=0))
print("-------------------Model 3--------------------")
print(classification_report(y_test_model3, y_pred3, zero_division=0))