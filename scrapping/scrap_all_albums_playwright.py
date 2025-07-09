# scrapping/scrap_all_albums_playwright.py

import os
import json
import csv
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

BASE           = "https://www.bdovore.com"
START          = f"{BASE}/browser?chbrowse=ser&let=&rb_browse=ser&offset=0"
HERE           = os.path.dirname(__file__)
URLS_FILE      = os.path.join(HERE, "seen_urls.json")
CSV_FILE       = os.path.join(HERE, "all_albums.csv")
PAGE_IDX_FILE  = os.path.join(HERE, "last_page.txt")

# Rotation d’User-Agent
UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/16.4 Safari/605.1.15",
]

REQ_HDRS = {
    "Accept-Language": "fr-FR,fr;q=0.9"
}

def load_state():
    seen = set()
    if os.path.exists(URLS_FILE):
        with open(URLS_FILE, "r", encoding="utf-8") as f:
            seen.update(json.load(f))
    scraped = set()
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                scraped.add(row["url"])
    return seen, scraped

def save_urls(seen):
    with open(URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)

def load_page_idx():
    if os.path.exists(PAGE_IDX_FILE):
        with open(PAGE_IDX_FILE) as f:
            return int(f.read().strip())
    return 1

def save_page_idx(page_num):
    with open(PAGE_IDX_FILE, "w") as f:
        f.write(str(page_num))

def ensure_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "url", "titre", "note", "nb_notes", "genre",
                "auteur", "publisher", "synopsis"
            ])
            writer.writeheader()

def make_page(browser: Browser) -> Page:
    # crée un nouveau contexte non-persistent
    context: BrowserContext = browser.new_context(
        user_agent=random.choice(UA_LIST),
        extra_http_headers=REQ_HDRS,
        locale="fr-FR",
        viewport={"width": 1280, "height": 800}
    )
    # bloquer CSS/images/fonts
    context.route("**/*", lambda route, req:
        route.abort() if req.resource_type in ["image","stylesheet","font"]
                      else route.continue_())
    page: Page = context.new_page()
    return page

def collect_album_urls(seen, start_page):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = make_page(browser)

        page.goto(START)
        page.wait_for_selector("div[onclick*='xhr_level2']", timeout=15000)

        # monter à la page de reprise si besoin
        page_num = 1
        while page_num < start_page:
            nxt = page.query_selector("a:has-text('Suivant')")
            if not nxt:
                break
            nxt.click()
            page.wait_for_load_state("networkidle")
            time.sleep(random.uniform(0.5,1.5))
            page_num += 1

        # pagination complète
        while True:
            # injecter toutes les séries (XHR)
            try:
                page.eval_on_selector_all(
                    "div[onclick*='xhr_level2']",
                    "els => els.forEach(e => e.click())"
                )
            except:
                pass
            time.sleep(random.uniform(0.5,1.5))

            soup = BeautifulSoup(page.content(), "lxml")
            before = len(seen)
            for div in soup.select("div[id^='onglet_div_xhr_']"):
                for a in div.select("a[href*='Album?id_tome=']"):
                    href = a["href"].split("&",1)[0]
                    seen.add(urljoin(BASE, href))
            if len(seen) > before:
                save_urls(seen)

            print(f"Page {page_num}: total URLs = {len(seen)}")
            save_page_idx(page_num + 1)

            nxt = page.query_selector("a:has-text('Suivant')")
            if not nxt:
                break
            nxt.click()
            page.wait_for_load_state("networkidle")
            time.sleep(random.uniform(0.5,1.5))
            page_num += 1

        # fermer tous les contextes
        browser.close()
    return seen

def scrape_album(url, scraped, writer):
    if url in scraped:
        return
    for attempt in range(3):
        try:
            r = requests.get(
                url + "&mobile=&frame=iframe",
                headers={"User-Agent": random.choice(UA_LIST), **REQ_HDRS},
                timeout=10
            )
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "lxml")

            def txt(sel):
                t = soup.select_one(sel)
                return t.get_text(" ", strip=True) if t else ""

            def att(sel,name):
                t = soup.select_one(sel)
                return t[name].strip() if t and t.has_attr(name) else ""

            row = {
                "url":       url,
                "titre":     txt('h3 span[itemprop="name"]'),
                "note":      att('div[itemprop="aggregateRating"] meta[itemprop="ratingValue"]',"content"),
                "nb_notes":  txt('div[itemprop="aggregateRating"] span[itemprop="reviewCount"]'),
                "genre":     txt('span[itemprop="genre"]'),
                "auteur":    txt('a[itemprop="author"]'),
                "publisher": txt('span[itemprop="publisher"]') or txt('select#sel_edition option[selected]'),
                "synopsis":  " ".join(soup.select_one("div.synopsis font").stripped_strings)
                                  if soup.select_one("div.synopsis font") else "",
            }
            writer.writerow(row)
            print("✓", row["titre"])
            scraped.add(url)
            break
        except Exception as e:
            print(f"Retry {attempt+1}/3 for {url}: {e}")
            time.sleep(random.uniform(1,3))

if __name__ == "__main__":
    seen_urls, scraped_urls = load_state()
    start_page = load_page_idx()
    ensure_csv()

    all_urls = collect_album_urls(seen_urls, start_page)
    print(f"→ Total album URLs collected: {len(all_urls)}")

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "url","titre","note","nb_notes","genre",
            "auteur","publisher","synopsis"
        ])
        for u in all_urls:
            scrape_album(u, scraped_urls, writer)
            time.sleep(random.uniform(0.3,1.0))

    print("\n✔ Scraping terminé — CSV:", CSV_FILE)
    print("✔ URLs checkpoint :", URLS_FILE)
    print("✔ Page checkpoint :", PAGE_IDX_FILE)


