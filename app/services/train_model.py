import pandas as pd
from sklearn.svm import SVC
import joblib
import os

# Load data
df = pd.read_csv("app/data/data.csv")

# Pastikan column 'target' memang wujud
assert 'target' in df.columns, "Column 'target' not found in data!"

# Pisah feature dan target
X = df.drop('target', axis=1)
y = df['target']

# Pastikan feature names guna nama yang sama dengan waktu prediction!
print("Feature columns used for training:", list(X.columns))

# Train model
model = SVC()
model.fit(X, y)

# Save model
os.makedirs("app/data/models", exist_ok=True)
joblib.dump(model, "app/data/models/model_v1.pkl")
print("Model saved to app/data/models/model_v1.pkl!")
