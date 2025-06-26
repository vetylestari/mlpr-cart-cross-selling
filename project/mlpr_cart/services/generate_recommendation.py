import pandas as pd
import joblib
import ast
from datetime import datetime, timedelta
from sqlalchemy import text
from sklearn.linear_model import LogisticRegression
from project.mlpr_cart.data_pipeline.db import get_db_connection
import re

def safe_parse_category_list(x):
    if isinstance(x, str):
        return [s.strip() for s in re.split(r',\s*', x)]
    return []

# Load model & encoder
model = joblib.load("app/models/model.joblib")
encoder = joblib.load("app/models/encoder.joblib")
product_meta = pd.read_parquet("data/product_metadata.parquet")
category_pairs = pd.read_csv("data/category_pairs.csv")
category_pairs["category_paired"] = category_pairs["category_paired"].apply(safe_parse_category_list)

def fetch_recent_cart_products():
    query = text("""
        SELECT DISTINCT product_id
        FROM rns_cart
        WHERE date_in >= :since_date
    """)
    since_date = datetime.now() - timedelta(days=31)

    engine = get_db_connection()  
    with engine.connect() as conn:
        result = conn.execute(query, {"since_date": since_date})
        return [row[0] for row in result.fetchall()]


def get_candidate_recommendations(input_product):
    input_row = product_meta[product_meta["product_id"] == input_product]
    if input_row.empty:
        return None, None

    input_cat = input_row["category_name"].values[0]
    input_name = input_row["product_name"].values[0]

    # Ambil kategori pairing dari category_pairs
    paired_row = category_pairs[category_pairs["category_name"] == input_cat]
    if paired_row.empty:
        related_cats = product_meta["category_name"].value_counts().head(5).index.tolist()
    else:
        related_cats = paired_row.iloc[0]["category_paired"]

    # Filter kandidat
    candidates = product_meta[
        (product_meta["product_id"] != input_product) &
        (product_meta["category_name"].isin(related_cats))
    ].copy()

    # Tambahkan skor dummy jika X_test gagal atau hasil predict_proba kosong
    if candidates.empty:
        return input_name, []

    try:
        X_test = encoder.transform(candidates[["category_1", "category_2"]])
        probs = model.predict_proba(X_test)[:, 1]
        candidates["score"] = probs
    except Exception:
        candidates["score"] = 0.5  # fallback

    top = candidates.sort_values("score", ascending=False).head(10)
    return input_name, top["product_id"].tolist()


def update_recommendation_db(trigger_id, recommendations):
    now = datetime.now()
    engine = get_db_connection()  
    with engine.begin() as conn:
        conn.execute(text("""
            DELETE FROM machine_learning.rns_mlpr_cart rc WHERE rc.product_id_trigger = :pid
        """), {"pid": trigger_id})

        conn.execute(text("""
            INSERT INTO machine_learning.rns_mlpr_cart (product_id_trigger, recommended_product_ids, updated_at)
            VALUES (:pid, :rec, :updated)
        """), {
            "pid": trigger_id,
            "rec": recommendations,
            "updated": now
        })

def run_batch():
    product_ids = fetch_recent_cart_products()
    for pid in product_ids:
        input_name, recs = get_candidate_recommendations(pid)
        if recs:
            update_recommendation_db(pid, recs)
            print(f"✅ Updated for {pid} ({input_name}) → {len(recs)} recommendations")
        else:
            print(f"⚠️ No recommendations for {pid} ({input_name})")


if __name__ == "__main__":
    run_batch()