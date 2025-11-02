# scrape_bogleheads.py
import requests, os
from bs4 import BeautifulSoup

def scrape_thread(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    posts = soup.find_all('div', class_='content')
    return "\n\n".join(p.get_text(strip=True) for p in posts)

urls = [
    #"https://www.bogleheads.org/forum/viewtopic.php?t=406905",
    # Add more trusted URLs
    "https://www.bogleheads.org/wiki/Main_Page",
]

os.makedirs("data", exist_ok=True)
for i, url in enumerate(urls):
    text = scrape_thread(url)
    with open(f"data/thread_{i}.txt", "w") as f:
        f.write(text)

