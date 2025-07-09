# scrapping/scrap_all_async.py

import asyncio
import csv
import html
import re
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

BASE           = "https://www.bdovore.com"
LIST_URL_TPL   = BASE + "/browser?chbrowse=ser&let=&rb_browse=ser&offset={offset}"
XHR_URL_TPL    = BASE + "/browser/xhr_level2?lev_id={lev_id}&totalRows={total}&chbrowse=ser&let=&rb_browse=ser"
TOTAL_ROWS     = 56637
PAGE_SIZE      = 25
OUTPUT_CSV     = "scrapping/first_all_albums_async.csv"

async def fetch_listing(session: aiohttp.ClientSession, offset: int) -> list[str]:
    """Récupère tous les lev_id présents sur la page de listing à cet offset."""
    url = LIST_URL_TPL.format(offset=offset)
    async with session.get(url) as resp:
        text = await resp.text()
    soup = BeautifulSoup(text, "lxml")
    lev_ids = []
    for tag in soup.find_all("div", onclick=True):
        un = html.unescape(tag["onclick"])
        m  = re.search(r"\$\.get\(\"[^\"]*xhr_level2\?lev_id=(\d+)", un)
        if m:
            lev_ids.append(m.group(1))
    return lev_ids

async def fetch_tome(session: aiohttp.ClientSession, lev_id: str) -> dict:
    """Appelle l’XHR du lev_id, parse le fragment HTML et renvoie la ligne CSV."""
    url = XHR_URL_TPL.format(lev_id=lev_id, total=TOTAL_ROWS)
    headers = {"X-Requested-With": "XMLHttpRequest"}
    async with session.get(url, headers=headers) as resp:
        text = await resp.text()
    soup = BeautifulSoup(text, "lxml")

    def txt(sel):
        t = soup.select_one(sel)
        return t.get_text(" ", strip=True) if t else ""

    def att(sel, attr):
        t = soup.select_one(sel)
        return t[attr].strip() if t and t.has_attr(attr) else ""

    # extraire l’ID du tome pour reconstruire l’URL
    pid = None
    id_tag = soup.select_one("span.petite_police")
    if id_tag:
        m2 = re.search(r"ID-BDovore\s*:\s*(\d+)", id_tag.get_text())
        if m2:
            pid = m2.group(1)

    return {
        "url":       f"{BASE}/Album?id_tome={pid}" if pid else "",
        "titre":     txt('span[itemprop="name"]'),
        "note":      att('meta[itemprop="ratingValue"]', "content"),
        "nb_notes":  txt('span[itemprop="reviewCount"]'),
        "genre":     txt('span[itemprop="genre"]'),
        "auteur":    txt('a[itemprop="author"]'),
        "publisher": txt('span[itemprop="publisher"]') 
                       or txt('select#sel_edition option[selected]'),
        "synopsis":  " ".join(soup.select_one("div.synopsis font").stripped_strings)
                       if soup.select_one("div.synopsis font") else "",
    }

async def main():
    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        # 1) On récupère tous les lev_id de toutes les pages
        offsets = range(0, TOTAL_ROWS, PAGE_SIZE)
        lev_id_tasks = [
            fetch_listing(session, off)
            for off in offsets
        ]
        pages_results = await asyncio.gather(*lev_id_tasks)
        lev_ids = [lid for page in pages_results for lid in page]
        lev_ids = list(dict.fromkeys(lev_ids))  # unique
        print(f"→ Total lev_id collectés : {len(lev_ids)}")

        # 2) On scrape chaque fragment XHR pour obtenir les données
        tome_tasks = [
            fetch_tome(session, lid)
            for lid in lev_ids
        ]
        rows = await asyncio.gather(*tome_tasks)

    # 3) On écrit le CSV
    fieldnames = ["url","titre","note","nb_notes","genre","auteur","publisher","synopsis"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✔ CSV enregistré : {OUTPUT_CSV}")

if __name__ == "__main__":
    asyncio.run(main())
