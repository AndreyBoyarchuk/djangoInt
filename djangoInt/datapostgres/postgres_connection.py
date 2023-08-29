# database.py
from dotenv import load_dotenv
import psycopg2
import os
from sqlalchemy import create_engine,text

load_dotenv()

def create_connection():
    # Connection details
    dbname = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')

    # Creating psycopg2 connection
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )

    except Exception as e:
        print("Connection failed:", e)
        return None

    # Creating SQLAlchemy engine using psycopg2 connection details
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")

    return engine

engine = create_connection()
if engine:
    with engine.connect() as connection:
        statement = text("SELECT version();")
        result = connection.execute(statement)
        version = result.fetchone()

print(version)



