# dual-book-advisor/scrapping/scrap_first25.py

import os, csv, time, re, html, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE      = "https://www.bdovore.com/"
# Notez les paramètres chbrowse, let et rb_browse !
LIST_URL  = BASE + "browser?chbrowse=ser&let=&rb_browse=ser&offset=0"
HEADERS   = {
    "User-Agent": "Mozilla/5.0 (dual-book-advisor/0.1)",
    "Referer":    LIST_URL,
}
AJAX_HDR  = {"X-Requested-With": "XMLHttpRequest"}

HERE      = os.path.dirname(os.path.abspath(__file__))
OUTPUT    = os.path.join(HERE, "first25_albums.csv")

session = requests.Session()
session.headers.update(HEADERS)
session.get(BASE, timeout=10)  # pose les cookies

def get_soup(url: str, ajax: bool=False) -> BeautifulSoup:
    hdrs = HEADERS.copy()
    if ajax:
        hdrs.update(AJAX_HDR)
    resp = session.get(url, headers=hdrs, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")

# 1) Charger la page complète avec les bons params
root = get_soup(LIST_URL)

# 2) Extraire tous les onclick XHR (xhr_level2)
iframe_tags = root.find_all(onclick=True)
xhr_urls = []
for tag in iframe_tags:
    js = html.unescape(tag["onclick"])
    m  = re.search(r'\$\.get\("([^"]*xhr_level2[^"]+)"', js)
    if m:
        xhr_urls.append(urljoin(BASE, m.group(1)))

# 3) Appeler ces XHR pour récupérer 25 URLs d'albums
album_urls = []
for xhr in xhr_urls:
    block = get_soup(xhr, ajax=True)
    for a in block.select('a[href*="Album?id_tome="]'):
        href = a["href"].split("&",1)[0]
        full = urljoin(BASE, href)
        if full not in album_urls:
            album_urls.append(full)
        if len(album_urls) >= 25:
            break
    if len(album_urls) >= 25:
        break

print("→ Albums trouvés :", len(album_urls))

# 4) Scraper chaque album et écrire le CSV
with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "url","titre","note","nb_notes","genre",
        "auteur","publisher","synopsis","cover_img"
    ])
    writer.writeheader()

    for url in album_urls:
        page = get_soup(url + "&mobile=&frame=iframe")
        txt  = lambda sel: (t:=page.select_one(sel)) and t.get_text(" ",strip=True) or ""
        att  = lambda sel,at: (t:=page.select_one(sel)) and t.get(at,"").strip() or ""

        row = {
            "url":      url,
            "titre":    txt('h3 span[itemprop="name"]'),
            "note":     att('div[itemprop="aggregateRating"] meta[itemprop="ratingValue"]',"content"),
            "nb_notes": txt('div[itemprop="aggregateRating"] span[itemprop="reviewCount"]'),
            "genre":    txt('span[itemprop="genre"]'),
            "auteur":   txt('a[itemprop="author"]'),
            "publisher":txt('span[itemprop="publisher"]')
                          or txt('select#sel_edition option[selected]'),
            "synopsis": " ".join(page.select_one("div.synopsis font").stripped_strings)
                          if page.select_one("div.synopsis font") else "",
            "cover_img":att("#couv img","src"),
        }
        writer.writerow(row)
        print("✓", row["titre"])
        time.sleep(0.8)

print("\n✔ CSV enregistré :", OUTPUT)

