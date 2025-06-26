# data_pipeline/fetch_data.py

import pandas as pd
import psycopg2
import pyarrow as pa
import pyarrow.parquet as pq
from decouple import config
from pathlib import Path

def fetch_cart_data():
    conn = psycopg2.connect(
        host=config('DB_HOST'),
        database=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        port=config('DB_PORT')
    )

    query = """
        SELECT
            rc.user_id,
            rc.cart_id,
            rc.product_id,
            rc.product_sku_id,
            rc.date_in + interval '7 hour' AS cart_session_date
        FROM rns_cart rc 
        WHERE rc.date_in BETWEEN now() - interval '6 month' AND now()
        AND rc.cart_selected = 1
        ORDER BY rc.user_id ASC;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    table = pa.Table.from_pandas(df)
    pq.write_table(table, "data/cart_selected.parquet")
    print(f"✅ Saved {len(df)} rows to cart_selected.parquet")

def fetch_product_metadata():
    conn = psycopg2.connect(
        host=config('DB_HOST'),
        database=config('DB_NAME'),
        user=config('DB_USER'),
        password=config('DB_PASSWORD'),
        port=config('DB_PORT')
    )

    query = """
        SELECT
            rp.product_id,
            rps.product_sku_id,
            rp.category_id,
            rp.product_name,
            rc.category_name
        FROM rns_product rp
        JOIN rns_product_sku rps ON rp.product_id = rps.product_id 
        JOIN rns_category rc ON rp.category_id = rc.category_id;
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    table = pa.Table.from_pandas(df)
    pq.write_table(table, "data/product_metadata.parquet")
    print(f"✅ Saved {len(df)} rows to product_metadata.parquet")

if __name__ == "__main__":
    Path("data").mkdir(parents=True, exist_ok=True)
    fetch_cart_data()
    fetch_product_metadata()