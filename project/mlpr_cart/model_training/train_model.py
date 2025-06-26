# model_training/train_model.py

import pandas as pd
import joblib
from scipy import sparse
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from pathlib import Path

# Load features and labels
X = sparse.load_npz("data/features.npz")
y_df = pd.read_parquet("data/labels.parquet")
y = y_df["label"].values

# Train model
model = LogisticRegression(max_iter=500, class_weight="balanced")
model.fit(X, y)

# Save model
Path("app/models").mkdir(parents=True, exist_ok=True)
joblib.dump(model, "app/models/model.joblib")
print("✅ Model saved to app/models/model.joblib")

# Evaluate
y_pred = model.predict(X)
print("\n📊 Classification Report:")
print(classification_report(y, y_pred))