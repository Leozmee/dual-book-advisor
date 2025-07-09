# scrapping/debug_listing.py
import html, re, requests
from bs4 import BeautifulSoup

BASE = "https://www.bdovore.com/"
LIST = BASE + "browser?chbrowse=ser&let=&rb_browse=ser&offset=0"
HEAD = {
    "User-Agent": "Mozilla/5.0 (dual-book-advisor/0.1)",
    "Referer":    LIST,
}

s = requests.Session()
s.headers.update(HEAD)
s.get(BASE, timeout=10)

resp = s.get(LIST, timeout=15)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "lxml")

tags = soup.find_all(onclick=True)
print("Nombre de blocs onclick trouvés :", len(tags))
for tag in tags[:3]:
    js = html.unescape(tag["onclick"])
    print("\n--- onclick brut ---")
    print(js[:200], "…")
    m = re.search(r'\$\.get\("([^"]*xhr_level2[^"]+)"', js)
    print("XHR-level2 URL détectée :", m.group(1) if m else "aucune")

