from decouple import config
import sqlalchemy as sa

def get_db_connection():
    db_url = config("DATABASE_URL", default="sqlite:///./test.db")

    if db_url.startswith("sqlite"):
        engine = sa.create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = sa.create_engine(db_url)

    return engine