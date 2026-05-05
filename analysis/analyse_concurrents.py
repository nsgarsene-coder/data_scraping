import os
import pandas as pd
import matplotlib.pyplot as plt

import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database", "amazon.db")

conn = sqlite3.connect(DB_PATH)

df_test = pd.read_sql("SELECT COUNT(*) AS nb FROM products", conn)
print(df_test)

conn.close()


# ===============================
# Chargement du CSV clean
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

csv_path = os.path.join(
    BASE_DIR,
    "..",
    "exports",
    "amazon_concurrents_clean.csv"
)

df = pd.read_csv(csv_path)
# ===============================
# Nettoyage de la colonne rating
# ===============================
df["rating_clean"] = (
    df["rating"]
    .astype(str)
    .str.replace(",", ".")                # 4,5 → 4.5
    .str.extract(r"(\d+\.\d+|\d+)")        # extrait le nombre
)

df["rating_clean"] = pd.to_numeric(
    df["rating_clean"],
    errors="coerce"
)


# ===============================
# Affichage en tableau lisible
# ===============================
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 150)

print("\n Aperçu général :\n")
print(df.head())

print("\n Statistiques descriptives (prix, notes) :\n")
print(df.describe())
print("\n Marques les plus présentes :\n")
print(
    df["brand"]
    .value_counts()
    .head(10)
)
print("\n Prix moyen par marque :\n")
print(
    df.groupby("brand")["price"]
    .mean()
    .sort_values()
)
print("\n Note moyenne par marque :\n")
print(
    df.groupby("brand")["rating_clean"]
    .mean()
    .sort_values(ascending=False)
)
df.groupby("brand")["price"].mean().sort_values().plot(
    kind="barh",
    title="Prix moyen par marque",
    figsize=(10, 6)
)

plt.xlabel("Prix")
plt.ylabel("Marque")
plt.tight_layout()
plt.show()
print("\n Aperçu ratings nettoyés :\n")
print(df[["rating", "rating_clean"]].head(10))