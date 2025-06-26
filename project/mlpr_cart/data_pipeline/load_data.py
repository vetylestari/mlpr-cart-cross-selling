import pandas as pd

product_meta = pd.read_parquet("data/product_metadata.parquet")
print(product_meta.head(5))
print(product_meta.columns)
print(product_meta["product_id"].unique()[:10])