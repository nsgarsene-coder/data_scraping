import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- CONFIGURATION ---
MARQUE_CIBLE = "Logitech"
PLATEFORME = "E-commerce"
SITE_SOURCE = "Amazon FR"
CATEGORIE = "Informatique & Accessoires" # Tu peux adapter selon le besoin
BASE_URL = "https://www.amazon.fr/s?k=logitech&page={}"
NB_PAGES = 3

options = Options()
options.add_argument("--start-maximized")
# Désactive les images pour aller plus vite si besoin
# options.add_argument('--blink-settings=imagesEnabled=false')

driver = webdriver.Chrome(options=options)

# --- PRÉPARATION DU FICHIER CSV ---
# On ajoute toutes les colonnes demandées
colonnes = [
    "nom_produit", "marque", "prix", "categorie", "plateforme", 
    "site_source", "url_produit", "note", "nombre_avis", "disponibilite", "page"
]

with open("amazon_logitech_complet.csv", "w", newline="", encoding="utf-8") as fichier:
    writer = csv.writer(fichier)
    writer.writerow(colonnes)

    for page in range(1, NB_PAGES + 1):
        url = BASE_URL.format(page)
        print(f"🔍 Scraping approfondi {MARQUE_CIBLE} - Page {page}...")

        driver.get(url)
        time.sleep(5) 

        # On cible les conteneurs de produits principaux
        produits = driver.find_elements(By.CSS_SELECTOR, "div.s-result-item[data-component-type='s-search-result']")

        for p in produits:
            try:
                # 1. Nom du produit
                nom = p.find_element(By.CSS_SELECTOR, "h2 span").text

                # 2. Prix
                try:
                    entier = p.find_element(By.CSS_SELECTOR, ".a-price-whole").text
                    centimes = p.find_element(By.CSS_SELECTOR, ".a-price-fraction").text
                    prix = f"{entier},{centimes}€"
                except:
                    prix = "N/A"

                # 3. Note (ex: 4.5)
                try:
                    note_brute = p.find_element(By.CSS_SELECTOR, ".a-icon-alt").get_attribute("innerHTML")
                    note = note_brute.split(" ")[0] # Récupère juste le chiffre
                except:
                    note = "N/A"

                # 4. Nombre d'avis
                try:
                    avis = p.find_element(By.CSS_SELECTOR, "span.a-size-base.s-underline-text").text
                    avis = avis.replace("(", "").replace(")", "").replace(".", "")
                except:
                    avis = "0"

                # 5. URL Produit
                try:
                    lien = p.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
                except:
                    lien = "N/A"

                # 6. Disponibilité (Stock)
                # Sur la liste de recherche, Amazon affiche souvent "Il n'en reste que X" ou rien (si en stock)
                try:
                    stock_text = p.find_element(By.CSS_SELECTOR, ".s-label-number-stock").text
                    dispo = f"Limité : {stock_text}"
                except:
                    dispo = "En stock" if prix != "N/A" else "Indisponible"

                # Écriture de la ligne avec les infos fixes et capturées
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

            except Exception as e:
                # Si un produit est une publicité mal formatée, on l'ignore
                continue

        time.sleep(2)

driver.quit()
print(f"✅ Terminé ! Toutes les informations pour {MARQUE_CIBLE} sont dans le fichier.")