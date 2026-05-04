import os
import pandas as pd

# ===============================
# 1. Chargement du fichier
# ===============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

csv_path = os.path.join(
    BASE_DIR,
    "amazon_concurrents_20260504_174926.csv"
)

df = pd.read_csv(csv_path)

print(" CSV chargé avec succès\n")

# ===============================
# 2. Détection par nom de colonne
# ===============================
def detect_by_name(col_name):
    name = col_name.lower()

    if "date" in name:
        return "date"
    if "price" in name or "prix" in name:
        return "numerique"
    if "mail" in name or "email" in name:
        return "email"
    if name == "id" or name.endswith("_id"):
        return "identifiant"

    return None


# ===============================
# 3. Détection par contenu
# ===============================
def detect_column_types(df):
    detected = {}

    for col in df.columns:
        # priorité au nom
        type_from_name = detect_by_name(col)
        if type_from_name:
            detected[col] = type_from_name
            continue

        # analyse du contenu
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            detected[col] = "date"
        elif pd.api.types.is_numeric_dtype(df[col]):
            detected[col] = "numerique"
        elif df[col].astype(str).str.contains("@").mean() > 0.8:
            detected[col] = "email"
        elif df[col].nunique(dropna=True) == len(df):
            detected[col] = "identifiant"
        else:
            detected[col] = "texte"

    return detected


# ===============================
# 4. Exécution
# ===============================
colonnes_detectees = detect_column_types(df)

print(" Colonnes détectées :\n")
for col, col_type in colonnes_detectees.items():
    print(f"{col} ➜ {col_type}")
def clean_dataframe(df, column_types):
    df_clean = df.copy()

    for col, col_type in column_types.items():

        if col_type == "numerique":
            df_clean[col] = (
                df_clean[col]
                .astype(str)
                .str.replace(",", ".")
                .str.replace(r"[^\d\.]", "", regex=True)
            )
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

        elif col_type == "date":
            df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce")

        elif col_type == "texte":
            df_clean[col] = (
                df_clean[col]
                .astype(str)
                .str.strip()
            )

    return df_clean
# ===============================
# 5. Nettoyage
# ===============================
df_clean = clean_dataframe(df, colonnes_detectees)

# ===============================
# 6. Export du CSV clean
# ===============================
clean_csv_path = os.path.join(
    BASE_DIR,
    "amazon_concurrents_20260504_174926_clean.csv"
)

df_clean.to_csv(clean_csv_path, index=False, encoding="utf-8")

print("\n CSV CLEAN créé avec succès :")
print(clean_csv_path)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 120)

print(df_clean.head())
