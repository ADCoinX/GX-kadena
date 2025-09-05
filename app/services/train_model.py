import pandas as pd
from sklearn.svm import SVC
import joblib

df = pd.read_csv("app/data/data.csv")

# Pastikan columns: 'tx_count', 'age_days', 'balance', 'related_address_count', 'scam_flag', 'target'
X = df[['tx_count', 'age_days', 'balance', 'related_address_count', 'scam_flag']]
y = df['target']

model = SVC()
model.fit(X, y)

joblib.dump(model, "app/data/models/model_v1.pkl")
print("Model saved!")
