# test_one_album.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pprint import pprint

TOME_ID     = "111578"
BASE        = "https://www.bdovore.com/"
ALBUM_FULL  = f"{BASE}Album?id_tome={TOME_ID}"                # page COMPLETE
ALBUM_FRAME = ALBUM_FULL + "&mobile=&frame=iframe"           # page rapide sans #simil

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (dual-book-advisor/0.1)",
    "Referer":    "https://www.bdovore.com/browser"
})
# prime le cookie-jar
session.get(BASE, timeout=10)

def get_soup(url: str) -> BeautifulSoup:
    r = session.get(url, timeout=10)
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")

# --- 1) extraction des champs principaux depuis la FRAME (plus rapide) ---
soup_frame = get_soup(ALBUM_FRAME)

def txt(soup, sel):
    t = soup.select_one(sel)
    return t.get_text(" ", strip=True) if t else ""

def attr(soup, sel, name):
    t = soup.select_one(sel)
    return t[name].strip() if t and t.has_attr(name) else ""

data = {
    "titre":     txt(soup_frame, 'h3 span[itemprop="name"]'),
    "note":      attr(soup_frame, 'div[itemprop="aggregateRating"] meta[itemprop="ratingValue"]', "content"),
    "nb_notes":  txt(soup_frame, 'div[itemprop="aggregateRating"] span[itemprop="reviewCount"]'),
    "genre":     txt(soup_frame, 'span[itemprop="genre"]'),
    "auteur":    txt(soup_frame, 'a[itemprop="author"]'),
    "publisher": txt(soup_frame, 'span[itemprop="publisher"]')
                   or txt(soup_frame, 'select#sel_edition option[selected]'),
    "synopsis":  " ".join(soup_frame.select_one("div.synopsis font").stripped_strings)
                   if soup_frame.select_one("div.synopsis font") else "",
    "cover_img": attr(soup_frame, "#couv img", "src"),
}

# --- 2) reload du Referer, et fetch de la page FULL pour le bloc #simil ---
session.headers.update({"Referer": ALBUM_FULL})
soup_full = get_soup(ALBUM_FULL)

# debug : affiche le HTML de #simil
bloc = soup_full.select_one("div#simil")
print("=== HTML de #simil ===")
print(bloc.prettify() if bloc else "Aucun bloc #simil trouvé !")

# extraction des suggestions (liens image cliquables)
suggestions = []
for a in bloc.select("a[href*='Album?id_tome=']"):
    img = a.find("img")
    if not img:
        continue

    # URL absolue de la fiche suggérée
    href = a["href"]
    sug_url = urljoin(BASE, href.split("&")[0])

    # parse la fiche complète du titre suggéré
    sub = get_soup(sug_url)
    title = txt(sub, 'h3 span[itemprop="name"]')
    author = txt(sub, 'a[itemprop="author"]')
    publisher = txt(sub, 'span[itemprop="publisher"]') \
                or txt(sub, 'select#sel_edition option[selected]')

    # ignore si c'est le même titre
    if title and title != data["titre"]:
        suggestions.append({
            "titre":     title,
            "auteur":    author,
            "publisher": publisher
        })

data["suggestions"] = suggestions

# --- 3) Résultat final ---
pprint(data)
# scrapping/scrap_first25.py
import csv
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE       = "https://www.bdovore.com/"
LIST_URL   = BASE + "browser?offset=0"         # ← sans &frame
OUTPUT_CSV = "scrapping/first25.csv"
HEADERS    = {
    "User-Agent": "Mozilla/5.0 (dual-book-advisor/0.1)",
    "Referer":    "https://www.bdovore.com/browser"
}

session = requests.Session()
session.headers.update(HEADERS)
session.get(BASE, timeout=10)  # pose les cookies

def get_soup(url):
    r = session.get(url, timeout=15)
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")

# 1) On récupère la page de listing "full" pour y trouver les onclick XHR
soup = get_soup(LIST_URL)
xhr_urls = []
for div in soup.find_all("div", onclick=True):
    m = re.search(r'\$\(.*?\)\.get\("([^"]+xhr_level2[^"]+)"', div["onclick"])
    if m:
        xhr_urls.append(urljoin(BASE, m.group(1)))

# 2) On parcourt ces XHR pour extraire les liens de tomes (stop à 25)
vol_urls = []
for xhr in xhr_urls:
    soup_xhr = get_soup(xhr)
    for a in soup_xhr.select('a[href*="Album?id_tome="]'):
        href = a["href"].split("&",1)[0]
        full = urljoin(BASE, href)
        if full not in vol_urls:
            vol_urls.append(full)
        if len(vol_urls) >= 25:
            break
    if len(vol_urls) >= 25:
        break

print(f"→ {len(vol_urls)} tomes collectés (les 25 premiers).")

# 3) On scrape chaque tome et on écrit le CSV
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "url","titre","note","nb_notes","genre",
        "auteur","publisher","synopsis","cover_img"
    ])
    writer.writeheader()

    for url in vol_urls:
        # on prend la version frame pour le contenu
        soup_a = get_soup(url + "&mobile=&frame=iframe")

        def txt(sel):
            t = soup_a.select_one(sel)
            return t.get_text(" ", strip=True) if t else ""

        def attr(sel, name):
            t = soup_a.select_one(sel)
            return t[name].strip() if t and t.has_attr(name) else ""

        row = {
            "url":      url,
            "titre":    txt('h3 span[itemprop="name"]'),
            "note":     attr('div[itemprop="aggregateRating"] meta[itemprop="ratingValue"]', "content"),
            "nb_notes": txt('div[itemprop="aggregateRating"] span[itemprop="reviewCount"]'),
            "genre":    txt('span[itemprop="genre"]'),
            "auteur":   txt('a[itemprop="author"]'),
            "publisher": (
                txt('span[itemprop="publisher"]')
                or txt('select#sel_edition option[selected]')
            ),
            "synopsis": " ".join(
                            soup_a.select_one("div.synopsis font").stripped_strings
                        ) if soup_a.select_one("div.synopsis font") else "",
            "cover_img": attr("#couv img", "src"),
        }
        writer.writerow(row)
        print(f"✓ {row['titre']}")
        time.sleep(1)  # politeness

print(f"\n✔ Terminé : {OUTPUT_CSV} contient {len(vol_urls)} enregistrements.")




