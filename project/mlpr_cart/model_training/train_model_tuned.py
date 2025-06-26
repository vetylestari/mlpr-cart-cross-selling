# model_training/train_model_tuned.py

import pandas as pd
import joblib
from scipy import sparse
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report
from pathlib import Path

# Load features and labels
X = sparse.load_npz("data/features.npz")
y_df = pd.read_parquet("data/labels.parquet")
y = y_df["label"].values

# Split train-test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Hyperparameter tuning
param_grid = {
    "C": [0.01, 0.1, 1, 10],
    "penalty": ["l2"],
    "solver": ["liblinear"]
}

grid = GridSearchCV(
    LogisticRegression(max_iter=500, class_weight="balanced"),
    param_grid,
    scoring=["f1", "roc_auc", "precision", "recall"],
    refit="f1",  
    cv=3,
    n_jobs=-1,
    verbose=1
)

grid.fit(X_train, y_train)
print(f"✅ Best params: {grid.best_params_}")

# Save best model
best_model = grid.best_estimator_
Path("app/models").mkdir(parents=True, exist_ok=True)
joblib.dump(best_model, "app/models/model.joblib")
print("✅ Tuned model saved to app/models/model.joblib")

# Save metadata
metadata = {
    "model_type": "LogisticRegression",
    "best_params": grid.best_params_,
    "train_size": len(y_train),
    "test_size": len(y_test),
    "features_shape": X.shape,
    "timestamp": pd.Timestamp.now().isoformat()
}
joblib.dump(metadata, "app/models/model_metadata.joblib")
print("✅ Metadata saved to app/models/model_metadata.joblib")

# Evaluate
print("\n📊 Classification Report (Test Set):")
y_pred = best_model.predict(X_test)
print(classification_report(y_test, y_pred))