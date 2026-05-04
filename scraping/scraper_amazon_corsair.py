#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper Amazon France - Concurrents (Playwright + stealth)
Nécessite: 
    pip install playwright beautifulsoup4
    playwright install chromium

Playwright est plus rapide et plus discret que Selenium pour Amazon.
"""

import csv
import json
import time
import random
from datetime import datetime
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# =============================================================================
# CONFIGURATION
# =============================================================================
BRANDS = ["sony", "razer", "corsair", "hyperx", "logitech", "steelseries"]
BASE_URL = "https://www.amazon.fr/s?k={}&page={}"
MAX_PAGES = 5

# =============================================================================
# SCRAPING
# =============================================================================

def parse_products(html, brand):
    soup = BeautifulSoup(html, "html.parser")
    products = []
    containers = soup.select("[data-component-type='s-search-result']")
    if not containers:
        containers = soup.select(".s-result-item")

    for item in containers:
        try:
            title_elem = item.select_one("h2 a span") or item.select_one(".a-text-normal") or item.select_one("h2 span")
            title = title_elem.get_text(strip=True) if title_elem else "N/A"

            link_elem = item.select_one("h2 a") or item.select_one("a.a-link-normal")
            link = ""
            if link_elem and link_elem.get("href"):
                href = link_elem["href"]
                link = f"https://www.amazon.fr{href}" if href.startswith("/") else href

            price_whole = item.select_one(".a-price-whole")
            price_fraction = item.select_one(".a-price-fraction")
            price_symbol = item.select_one(".a-price-symbol")

            if price_whole and price_fraction:
                price = f"{price_symbol.get_text(strip=True) if price_symbol else '€'}{price_whole.get_text(strip=True).replace(',', '')},{price_fraction.get_text(strip=True)}"
            else:
                price_elem = item.select_one(".a-price .a-offscreen") or item.select_one(".a-price")
                price = price_elem.get_text(strip=True) if price_elem else "N/A"

            rating_elem = item.select_one("[aria-label*='étoiles']") or item.select_one(".a-icon-alt")
            rating = "N/A"
            if rating_elem:
                aria = rating_elem.get("aria-label", "")
                rating = aria if ("étoiles" in aria or "sur" in aria) else rating_elem.get_text(strip=True)

            reviews_elem = item.select_one("[aria-label*='évaluations']") or item.select_one("a[href*='reviews'] span")
            reviews = "N/A"
            if reviews_elem:
                text = reviews_elem.get_text(strip=True)
                if any(c.isdigit() for c in text):
                    reviews = text

            img_elem = item.select_one("img")
            image = img_elem.get("src", "") if img_elem else ""

            badge_elem = item.select_one(".a-badge-text")
            badge = badge_elem.get_text(strip=True) if badge_elem else ""

            if title != "N/A" and len(title) > 5:
                products.append({
                    "brand": brand,
                    "title": title,
                    "price": price,
                    "rating": rating,
                    "reviews": reviews,
                    "link": link,
                    "image": image,
                    "badge": badge,
                    "scraped_at": datetime.now().isoformat()
                })
        except Exception:
            continue
    return products


def scrape_brand(page, brand):
    all_products = []
    print(f"\n🔍 Scraping: {brand.upper()}")

    for p in range(1, MAX_PAGES + 1):
        url = BASE_URL.format(quote_plus(brand), p)
        print(f"  📄 Page {p}/{MAX_PAGES}")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            time.sleep(random.uniform(2, 4))

            # Scroll humain
            for _ in range(3):
                page.mouse.wheel(0, random.randint(400, 800))
                time.sleep(random.uniform(0.5, 1.5))

            # Attendre les résultats
            page.wait_for_selector("[data-component-type='s-search-result']", timeout=10000)
            html = page.content()

            # Détection CAPTCHA
            if "captcha" in html.lower() or "robot" in html.lower() or "enter the characters" in html.lower():
                print("  🛑 CAPTCHA ! Résous-le dans le navigateur, puis appuie sur ENTREE ici...")
                input("  ⏳ En attente...")
                html = page.content()

            products = parse_products(html, brand)
            if not products:
                print(f"  ⚠️ Aucun produit")
                break

            all_products.extend(products)
            print(f"  ✅ {len(products)} produits")

        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            break

        time.sleep(random.uniform(3, 6))

    print(f"  📊 Total {brand}: {len(all_products)}")
    return all_products


def save_data(products):
    if not products:
        print("Aucun produit.")
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"amazon_concurrents_{timestamp}.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=products[0].keys())
        writer.writeheader()
        writer.writerows(products)
    with open(f"amazon_concurrents_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"💾 Fichiers sauvegardés: amazon_concurrents_{timestamp}.csv/.json")


def main():
    print("=" * 60)
    print("🛒 AMAZON SCRAPER — PLAYWRIGHT EDITION")
    print("=" * 60)

    all_products = []

    with sync_playwright() as p:
        # Lancer Chromium avec stealth
        browser = p.chromium.launch(
            headless=False,  # Mettre True quand ça marchera
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process"
            ]
        )

        context = browser.new_context(
            locale="fr-FR",
            timezone_id="Europe/Paris",
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )

        # Masquer webdriver
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = { runtime: {} };
        """)

        page = context.new_page()

        try:
            for brand in BRANDS:
                products = scrape_brand(page, brand)
                all_products.extend(products)
        finally:
            browser.close()

    print("\n" + "=" * 60)
    print(f"🏁 TERMINÉ — {len(all_products)} produits")
    print("=" * 60)
    save_data(all_products)

    print("\n📈 RÉSUMÉ:")
    for brand in BRANDS:
        count = len([p for p in all_products if p["brand"] == brand])
        print(f"  • {brand.capitalize()}: {count}")

if __name__ == "__main__":
    main()