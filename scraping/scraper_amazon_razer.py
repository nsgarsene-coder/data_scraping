import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- CONFIGURATION ---
MARQUE_CIBLE = "Razer"
PLATEFORME = "E-commerce"
SITE_SOURCE = "Amazon FR"
CATEGORIE = "Gaming & Périphériques"
BASE_URL = "https://www.amazon.fr/s?k=razer&page={}"
NB_PAGES = 3

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

# --- PRÉPARATION DU FICHIER CSV ---
colonnes = [
    "nom_produit", "marque", "prix", "categorie", "plateforme", 
    "site_source", "url_produit", "note", "nombre_avis", "disponibilite", "page"
]

# On crée le fichier CSV spécifique à Razer
with open("amazon_razer_complet.csv", "w", newline="", encoding="utf-8") as fichier:
    writer = csv.writer(fichier)
    writer.writerow(colonnes)

    for page in range(1, NB_PAGES + 1):
        url = BASE_URL.format(page)
        print(f"🐍 Scraping approfondi {MARQUE_CIBLE} - Page {page}...")

        driver.get(url)
        time.sleep(5) # Sécurité pour le chargement

        # On cible uniquement les vrais résultats de recherche pour plus de précision
        produits = driver.find_elements(By.CSS_SELECTOR, "div.s-result-item[data-component-type='s-search-result']")

        for p in produits:
            try:
                # 1. Nom du produit
                nom = p.find_element(By.CSS_SELECTOR, "h2 span").text

                # 2. Prix (Gestion des entiers et centimes)
                try:
                    entier = p.find_element(By.CSS_SELECTOR, ".a-price-whole").text
                    centimes = p.find_element(By.CSS_SELECTOR, ".a-price-fraction").text
                    prix = f"{entier},{centimes}€"
                except:
                    prix = "N/A"

                # 3. Note (on extrait juste le chiffre)
                try:
                    note_brute = p.find_element(By.CSS_SELECTOR, ".a-icon-alt").get_attribute("innerHTML")
                    note = note_brute.split(" ")[0] 
                except:
                    note = "N/A"

                # 4. Nombre d'avis
                try:
                    avis = p.find_element(By.CSS_SELECTOR, "span.a-size-base.s-underline-text").text
                    avis = avis.replace("(", "").replace(")", "").replace(".", "").strip()
                except:
                    avis = "0"

                # 5. URL Produit
                try:
                    lien = p.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
                except:
                    lien = "N/A"

                # 6. Disponibilité
                try:
                    stock_text = p.find_element(By.CSS_SELECTOR, ".s-label-number-stock").text
                    dispo = f"Stock faible : {stock_text}"
                except:
                    dispo = "En stock" if prix != "N/A" else "Hors stock"

                # Écriture dans le CSV
                writer.writerow([
                    nom, 
                    MARQUE_CIBLE, 
                    prix, 
                    CATEGORIE, 
                    PLATEFORME, 
                    SITE_SOURCE, 
                    lien, 
                    note, 
                    avis, 
                    dispo, 
                    page
                ])

            except Exception:
                # Ignore les éléments publicitaires vides
                continue

        time.sleep(2)

driver.quit()
print(f"✅ Terminé ! Le fichier 'amazon_razer_complet.csv' contient toutes les infos demandées.")