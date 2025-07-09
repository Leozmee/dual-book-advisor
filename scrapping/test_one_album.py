


import requests
from bs4 import BeautifulSoup

TOME_ID = "111578"
BASE    = "https://www.bdovore.com/"
ALBUM_URL = (
    f"{BASE}Album?id_tome={TOME_ID}&mobile=&frame=iframe"
)

# 1) Crée une session pour conserver les cookies
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (dual-book-advisor/0.1)",
    "Referer":    "https://www.bdovore.com/browser"
})
# Pose les cookies indispensables
session.get(BASE, timeout=10)

# 2) Récupère la page de l’album
resp = session.get(ALBUM_URL, timeout=10)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "lxml")

# 3) Helpers pour extraire proprement
def get_text(sel, default=""):
    tag = soup.select_one(sel)
    return tag.get_text(" ", strip=True) if tag else default

def get_attr(sel, attr, default=""):
    tag = soup.select_one(sel)
    return tag[attr].strip() if tag and tag.has_attr(attr) else default

# 4) Extraction des champs
titre = get_text('h3 span[itemprop="name"]')
note  = get_attr(
    'div[itemprop="aggregateRating"] meta[itemprop="ratingValue"]',
    "content"
)
nb_notes = get_text(
    'div[itemprop="aggregateRating"] span[itemprop="reviewCount"]'
)
genre  = get_text('span[itemprop="genre"]')
auteur = get_text('a[itemprop="author"]')

# Publisher : span[itemprop="publisher"] OU select#sel_edition option[selected]
publisher_span = get_text('span[itemprop="publisher"]')
if publisher_span:
    publisher = publisher_span
else:
    publisher = get_text('select#sel_edition option[selected]')

# Synopsis
synopsis = ""
syn_el = soup.select_one("div.synopsis font")
if syn_el:
    synopsis = " ".join(syn_el.stripped_strings)

# Suggestions : uniquement les liens vers Album?id_tome=…
suggestions = [
    a["title"]
    for a in soup.select("div#simil a[title]")
    if "Album?id_tome=" in a["href"]
]

# Couverture
cover_img = get_attr("#couv img", "src")

# 5) Affiche le résultat
from pprint import pprint
pprint({
    "titre":       titre,
    "note":        note,
    "nb_notes":    nb_notes,
    "genre":       genre,
    "auteur":      auteur,
    "publisher":   publisher,
    "synopsis":    synopsis,
    "suggestions": suggestions,
    "cover_img":   cover_img,
})