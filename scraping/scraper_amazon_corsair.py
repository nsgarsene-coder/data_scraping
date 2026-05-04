import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# CONFIG
BASE_URL = "https://www.amazon.fr/s?k=corsair&page={}"
NB_PAGES = 3

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)

with open("amazon_corsair.csv", "w", newline="", encoding="utf-8") as fichier:
    writer = csv.writer(fichier)
    writer.writerow([
        "nom_produit",
        "prix",
        "note",
        "nombre_avis",
        "url_produit",
        "page"
    ])

    for page in range(1, NB_PAGES + 1):
        url = BASE_URL.format(page)
        print(f"Scraping page {page}...")

        driver.get(url)
        time.sleep(5)  # laisse charger la page

        produits = driver.find_elements(By.CSS_SELECTOR, "div.s-main-slot div.s-result-item")

        print("Produits trouvés :", len(produits))

        for p in produits:
            try:
                # Nom produit
                nom = p.find_element(By.CSS_SELECTOR, "h2 span").text

                # Prix (peut ne pas exister)
                try:
                    prix = p.find_element(By.CSS_SELECTOR, ".a-price-whole").text
                except:
                    prix = None

                # Note
                try:
                    note = p.find_element(By.CSS_SELECTOR, ".a-icon-alt").text
                except:
                    note = None

                # Nombre d'avis
                try:
                    avis = p.find_element(By.CSS_SELECTOR, ".a-size-base").text
                except:
                    avis = None

                # URL produit
                try:
                    lien = p.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
                except:
                    lien = None

                writer.writerow([nom, prix, note, avis, lien, page])

            except:
                continue

        time.sleep(2)

driver.quit()

print("✅ Scraping Amazon terminé !")