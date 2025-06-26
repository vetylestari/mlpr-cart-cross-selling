# data_pipeline/generate_pairs.py

import pandas as pd
from itertools import combinations
from pathlib import Path
from datetime import datetime

# Load data
cart_df = pd.read_parquet("data/cart_selected.parquet")

# Buat kolom session_date dari date_in
cart_df["session_date"] = pd.to_datetime(cart_df["cart_session_date"]).dt.date

# Filter sesi yang punya >1 produk
session_counts = cart_df.groupby(["user_id", "session_date"])["product_id"].nunique()
valid_sessions = session_counts[session_counts > 1].index

valid_df = cart_df.set_index(["user_id", "session_date"]).loc[valid_sessions].reset_index()

# Generate positive pairs
positive_pairs = []
for (user_id, session_date), group in valid_df.groupby(["user_id", "session_date"]):
    product_ids = sorted(group.product_id.unique())
    for p1, p2 in combinations(product_ids, 2):
        positive_pairs.append((p1, p2))

positive_df = pd.DataFrame(positive_pairs, columns=["product_id_1", "product_id_2"])
positive_df = positive_df.drop_duplicates()
positive_df["label"] = 1
positive_df.to_parquet("data/positive_pairs.parquet", index=False)
print(f"✅ Saved {len(positive_df)} positive pairs")

# Generate negative pairs
all_products = cart_df.product_id.unique().tolist()
positive_set = set(map(tuple, positive_df[["product_id_1", "product_id_2"]].values))

import random
negatives = set()
while len(negatives) < len(positive_df):
    a, b = sorted(random.sample(all_products, 2))
    if (a, b) not in positive_set:
        negatives.add((a, b))

neg_df = pd.DataFrame(list(negatives), columns=["product_id_1", "product_id_2"])
neg_df["label"] = 0
neg_df.to_parquet("data/negative_pairs.parquet", index=False)
print(f"✅ Saved {len(neg_df)} negative pairs")