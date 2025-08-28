# app/services/train_model.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
import joblib, os

def train_and_save_model(path="app/data/models/model_v1.pkl"):
    # Buat data dummy
    X_train, y_train = make_classification(
        n_samples=500, n_features=5, n_classes=2, random_state=42
    )
    # Train model dummy
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)

    # Pastikan folder wujud
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    print(f"✅ Model siap! File di: {path}")

if __name__ == "__main__":
    train_and_save_model()
