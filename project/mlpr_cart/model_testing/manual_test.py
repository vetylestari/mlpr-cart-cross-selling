import pandas as pd
import joblib
import ast

# Load resources
model = joblib.load("app/models/model.joblib")
encoder = joblib.load("app/models/encoder.joblib")
product_meta = pd.read_parquet("data/product_metadata.parquet")
category_pairs = pd.read_csv("data/category_pairs.csv")
positive_pairs = pd.read_parquet("data/positive_pairs.parquet")

# Konversi kolom category_paired ke list
category_pairs["category_paired"] = category_pairs["category_paired"].apply(
    lambda x: [i.strip() for i in x.split(",")] if isinstance(x, str) else []
)
# 🔰 Ganti ID ini untuk testing
input_product = 220726

# Ambil metadata produk input
input_row = product_meta[product_meta["product_id"] == input_product]

if input_row.empty:
    print(f"❌ Product ID {input_product} not found in metadata.")
    print("🔁 Fallback: Tampilkan top-selling produk sebagai rekomendasi sementara.\n")

    fallback = product_meta.copy()
    fallback["score"] = 0.5  # Dummy score
    top_recommendations = fallback.sort_values("score", ascending=False).head(10)

    print(top_recommendations[["product_id", "product_sku_id", "product_name", "category_name", "score"]])

else:
    input_cat = input_row["category_name"].values[0]
    input_name = input_row["product_name"].values[0]

    print("🛒 Input:", input_product, "|", input_name, "|", input_cat)

    # Cek apakah produk ini punya pasangan dari training (positive_pairs)
    candidate_ids = positive_pairs[positive_pairs["product_id_1"] == input_product]["product_id_2"].unique()

    if len(candidate_ids) > 0:
        print("✅ Menggunakan pasangan dari historical positive pairs")

        candidates = product_meta[product_meta["product_id"].isin(candidate_ids)].copy()
        candidates["category_1"] = input_cat
        candidates["category_2"] = candidates["category_name"]

        X_test = encoder.transform(candidates[["category_1", "category_2"]])
        probs = model.predict_proba(X_test)[:, 1]
        candidates["score"] = probs

        top_recommendations = candidates.sort_values("score", ascending=False).head(10)

    else:
        print("⚠️ Tidak ditemukan pasangan historis. Gunakan kategori relevan sebagai fallback.")

        related_cats = category_pairs[category_pairs["category_name"] == input_cat]["category_paired"]
        related_cats = related_cats.values[0] if len(related_cats) > 0 else []

        if not related_cats:
            print(f"⚠️ No related categories found for: '{input_cat}'")
            related_cats = product_meta["category_name"].value_counts().head(5).index.tolist()

        candidates = product_meta[
            (product_meta["product_id"] != input_product)
            & (product_meta["category_name"].isin(related_cats))
        ].copy()

        if candidates.empty:
            print("⚠️ Tidak ada kandidat produk dari kategori relevan. Gunakan produk populer.")
            fallback = product_meta.copy()
            fallback["score"] = 0.5
            top_recommendations = fallback.sort_values("score", ascending=False).head(10)
        else:
            candidates["category_1"] = input_cat
            candidates["category_2"] = candidates["category_name"]

            X_test = encoder.transform(candidates[["category_1", "category_2"]])
            probs = model.predict_proba(X_test)[:, 1]
            candidates["score"] = probs

            top_recommendations = candidates.sort_values("score", ascending=False).head(10)

    # Tampilkan hasil akhir
    print("\n📦 Rekomendasi Produk")
    print(top_recommendations[["product_id", "product_sku_id", "product_name", "category_name", "score"]])

# import pandas as pd
# import joblib
# from sklearn.linear_model import LogisticRegression
# import ast

# # Load model & encoder
# model = joblib.load("app/models/model.joblib")
# encoder = joblib.load("app/models/encoder.joblib")
# product_meta = pd.read_parquet("data/product_metadata.parquet")
# category_pairs = pd.read_csv("data/category_pairs.csv")

# # Convert category_paired from string to list
# category_pairs["category_paired"] = category_pairs["category_paired"].apply(ast.literal_eval)

# # 🔰 Ganti ID ini untuk testing
# input_product = 223450

# # Ambil metadata produk
# input_row = product_meta[product_meta["product_id"] == input_product]

# if input_row.empty:
#     print(f"❌ Product ID {input_product} not found in metadata.")
#     print("🔁 Fallback: Tampilkan top-selling produk sebagai rekomendasi sementara.\n")

#     fallback = product_meta.copy()
#     fallback["score"] = 0.5  # dummy score
#     top_recommendations = fallback.sort_values("score", ascending=False).head(10)

#     print(top_recommendations[["product_id", "product_sku_id", "product_name", "category_name", "score"]])
# else:
#     input_cat = input_row["category_name"].values[0]
#     input_name = input_row["product_name"].values[0]

#     # 🔍 Cek apakah ada pairing kategori
#     related_cats = category_pairs[category_pairs["category_1"] == input_cat]["category_2"].tolist()

#     if not related_cats:
#         print(f"⚠️ No related categories found for: '{input_cat}'")
#         # fallback ke top-N kategori terbanyak
#         related_cats = product_meta["category_name"].value_counts().head(5).index.tolist()

#     # 🔎 Filter kandidat dari kategori relevan
#     candidates = product_meta[product_meta["product_id"] != input_product].copy()
#     candidates = candidates[candidates["category_name"].isin(related_cats)].copy()

#     if candidates.empty:
#         print("⚠️ Tidak ada produk dari kategori relevan ditemukan.")
#     else:
#         # Siapkan fitur
#         candidates["category_1"] = input_cat
#         candidates["category_2"] = candidates["category_name"]

#         X_test = encoder.transform(candidates[["category_1", "category_2"]])
#         probs = model.predict_proba(X_test)[:, 1]
#         candidates["score"] = probs

#         top_recommendations = candidates.sort_values("score", ascending=False).head(10)

#         print("\n📦 Rekomendasi Produk")
#         print("🛒 Input:", input_product, "|", input_name, "|", input_cat)
#         print(top_recommendations[["product_id", "product_sku_id", "product_name", "category_name", "score"]])