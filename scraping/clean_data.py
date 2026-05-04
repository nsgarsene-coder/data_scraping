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
