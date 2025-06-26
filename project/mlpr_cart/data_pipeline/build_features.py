# data_pipeline/build_features.py

import pandas as pd
from pathlib import Path
from sklearn.preprocessing import OneHotEncoder
import joblib
from scipy import sparse

# Load data
positive_df = pd.read_parquet("data/positive_pairs.parquet")
negative_df = pd.read_parquet("data/negative_pairs.parquet")
product_meta = pd.read_parquet("data/product_metadata.parquet")

# Gabungkan positif & negatif
all_pairs = pd.concat([positive_df, negative_df], ignore_index=True)

# Join metadata
merged = all_pairs.merge(product_meta, left_on="product_id_1", right_on="product_id", how="left")
merged = merged.rename(columns={"category_name": "category_1"}).drop(columns=["product_id"])

merged = merged.merge(product_meta, left_on="product_id_2", right_on="product_id", how="left")
merged = merged.rename(columns={"category_name": "category_2"}).drop(columns=["product_id"])

# Encode kategori
encoder = OneHotEncoder(handle_unknown="ignore")
cat_features = encoder.fit_transform(merged[["category_1", "category_2"]])

# Simpan fitur dan label
Path("data").mkdir(exist_ok=True)
sparse.save_npz("data/features.npz", cat_features)
merged[["product_id_1", "product_id_2", "label"]].to_parquet("data/labels.parquet", index=False)

# Simpan encoder
Path("app/models").mkdir(parents=True, exist_ok=True)
joblib.dump(encoder, "app/models/encoder.joblib")

print(f"✅ Features shape: {cat_features.shape}")
print("✅ Features & encoder saved.")