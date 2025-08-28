import pandas as pd
from sklearn.svm import SVC
import joblib

df = pd.read_csv("app/data/models/data.csv")
print(df.head())

X = df.drop('target', axis=1)
y = df['target']

model = SVC()
model.fit(X, y)
joblib.dump(model, "app/data/models/model_v1.pkl")
