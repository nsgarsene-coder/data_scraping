import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_PATH = os.path.join(
    BASE_DIR,
    "..",
    "exports",
    "amazon_concurrents_clean.csv"
)

DB_PATH = os.path.join(
    BASE_DIR,
    "amazon.db"
)

df = pd.read_csv(CSV_PATH)

# Connexion DB
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Création table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT,
    title TEXT,
    price REAL,
    rating REAL,
    reviews TEXT,
    link TEXT,
    image TEXT,
    badge TEXT,
    scraped_at TEXT
)
""")

# Insertion
df.to_sql("products", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

print(" Base de données créée et remplie avec succès")