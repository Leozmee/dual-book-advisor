import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://www.bdovore.com/"
LIST = BASE + "browser?offset=0"
HEAD = {
    "User-Agent":   "Mozilla/5.0 (dual-book-advisor/0.1)",
    "Referer":      LIST,
}

s = requests.Session()
s.headers.update(HEAD)
s.get(BASE, timeout=10)

# 1) page principale
r1 = s.get(LIST, timeout=10); r1.raise_for_status()
soup1 = BeautifulSoup(r1.text, "lxml")
iframe = soup1.find("iframe")
print("iframe trouvé :", iframe["src"] if iframe else "aucun iframe !")

# 2) charger l'iframe
if iframe:
    src = urljoin(BASE, iframe["src"])
    r2 = s.get(src, timeout=10); r2.raise_for_status()
    soup2 = BeautifulSoup(r2.text, "lxml")
    tags = soup2.find_all(onclick=True)
    print("onclick dans l'iframe :", len(tags))
    print("Exemple onclick :", tags[0]["onclick"][:200] if tags else "–")
