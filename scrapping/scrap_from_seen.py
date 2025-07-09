#!/usr/bin/env python3
# scrap_from_seen.py

import os
import json
import csv
import time
import random
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION ---

HERE      = os.path.dirname(__file__)
URLS_FILE = os.path.join(HERE, "seen_urls2.json")
OUTPUT    = os.path.join(HERE, "albums_from_seen.csv")

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.4 Safari/605.1.15",
]

HEADERS = {
    "Accept-Language": "fr-FR,fr;q=0.9"
}

# --- UTILITAIRES ---

def load_urls():
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_output():
    if not os.path.exists(OUTPUT):
        with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "url", "titre", "note", "nb_notes",
                "genre", "auteur", "publisher", "synopsis"
            ])
            writer.writeheader()

def scrape_album(url):
    """Retourne un dict avec les champs extraits de la page album."""
    headers = {
        **HEADERS,
        "User-Agent": random.choice(UA_LIST)
    }
    r = requests.get(url + "&mobile=&frame=iframe", headers=headers, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    def txt(sel):
        t = soup.select_one(sel)
        return t.get_text(" ", strip=True) if t else ""

    def att(sel, attr):
        t = soup.select_one(sel)
        return t[attr].strip() if t and t.has_attr(attr) else ""

    return {
        "url":       url,
        "titre":     txt('h3 span[itemprop="name"]'),
        "note":      att('div[itemprop="aggregateRating"] meta[itemprop="ratingValue"]', "content"),
        "nb_notes":  txt('div[itemprop="aggregateRating"] span[itemprop="reviewCount"]'),
        "genre":     txt('span[itemprop="genre"]'),
        "auteur":    txt('a[itemprop="author"]'),
        "publisher": txt('span[itemprop="publisher"]') or txt('select#sel_edition option[selected]'),
        "synopsis":  " ".join(soup.select_one("div.synopsis font").stripped_strings)
                      if soup.select_one("div.synopsis font") else "",
    }

# --- SCRIPT PRINCIPAL ---

def main():
    urls = load_urls()
    ensure_output()

    with open(OUTPUT, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "url", "titre", "note", "nb_notes",
            "genre", "auteur", "publisher", "synopsis"
        ])
        for i, url in enumerate(urls, start=1):
            try:
                data = scrape_album(url)
                writer.writerow(data)
                print(f"[{i}/{len(urls)}] ✓ {data['titre']}")
            except Exception as e:
                print(f"[{i}/{len(urls)}] ⚠️ Erreur sur {url}: {e}")
            # jitter entre chaque requête
            time.sleep(random.uniform(0.3, 1.0))

if __name__ == "__main__":
    main()
