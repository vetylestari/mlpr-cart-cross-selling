import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load metadata
meta = pd.read_parquet("data/product_metadata.parquet")

# Ambil daftar kategori unik
categories = sorted(meta["category_name"].dropna().unique().tolist())

# TF-IDF vektor untuk nama kategori
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(categories)

# Hitung cosine similarity antar kategori
similarity_matrix = cosine_similarity(tfidf_matrix)

pairs = []
threshold = 0.3  # bisa kamu adjust, makin tinggi makin mirip

for i in range(len(categories)):
    for j in range(i + 1, len(categories)):
        sim = similarity_matrix[i][j]
        if sim >= threshold:
            pairs.append({
                "category_1": categories[i],
                "category_2": categories[j],
                "similarity": round(sim, 3)
            })

df_pairs = pd.DataFrame(pairs).sort_values("similarity", ascending=False)
print(df_pairs.head(20))  # lihat top-20
df_pairs.to_csv("data/category_pairs_tfidf.csv", index=False)
