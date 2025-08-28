import pandas as pd
from sklearn.svm import SVC
import joblib
import os

df = pd.read_csv("app/data/models/data.csv")
X = df.drop('target', axis=1)
y = df['target']

model = SVC()
model.fit(X, y)

os.makedirs("app/data/models", exist_ok=True)
joblib.dump(model, "app/data/models/model_v1.pkl")
print("Model saved!")
