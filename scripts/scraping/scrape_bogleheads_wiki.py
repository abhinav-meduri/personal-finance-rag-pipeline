# scrape_bogleheads_wiki.py

import requests
from bs4 import BeautifulSoup
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36"
}

def scrape_wiki_page(url):
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        print(f"Request failed with code {res.status_code} for {url}")
        return None

    soup = BeautifulSoup(res.text, 'html.parser')

    # The wiki content is inside div#mw-content-text
    content_div = soup.find('div', id='mw-content-text')
    if not content_div:
        print(f"Content div not found for {url}")
        return None

    text = content_div.get_text(separator="\n", strip=True)
    return text

# List of Bogleheads wiki pages to scrape
urls = [
    "https://www.bogleheads.org/wiki/Main_Page",
    "https://www.bogleheads.org/wiki/Traditional_IRA",
    "https://www.bogleheads.org/wiki/Roth_IRA",
    "https://www.bogleheads.org/wiki/Asset_allocation",
    "https://www.bogleheads.org/wiki/Tax-efficient_fund_placement",
]

os.makedirs("wiki_data", exist_ok=True)

for i, url in enumerate(urls):
    text = scrape_wiki_page(url)
    if text:
        filename = f"wiki_data/page_{i}.txt"
        with open(filename, "w") as f:
            f.write(text)
        print(f"Saved: {filename}")
    else:
        print(f"Failed to scrape: {url}")

