# src/enricher.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from urllib.parse import quote_plus
from time import sleep
from tqdm import tqdm

OUT_ENRICH = Path("outputs/enriched/enriched_sample.csv")
OUT_ENRICH.parent.mkdir(parents=True, exist_ok=True)

def fetch_zaubacorp(cin):
    # ZaubaCorp search URL by CIN or name (site structure may change)
    url = f"https://www.zaubacorp.com/company/{quote_plus(cin)}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return {}
        soup = BeautifulSoup(resp.text, "lxml")
        # sample scraping - adjust to actual HTML
        data = {}
        # e.g. directors table
        directors = []
        for d in soup.select("table.directors tr"):
            tds = [td.get_text(strip=True) for td in d.find_all("td")]
            if tds:
                directors.append(" | ".join(tds))
        data['directors'] = "; ".join(directors)
        # industry/sector placeholder
        data['sector'] = soup.find(text="Industry").find_next().get_text(strip=True) if soup.find(text="Industry") else None
        return data
    except Exception as e:
        return {}

def enrich_list(cins):
    rows = []
    for cin in tqdm(cins):
        info = fetch_zaubacorp(cin)
        sleep(1)  # polite
        rows.append({"CIN":cin, "sector": info.get('sector'), "directors": info.get('directors'), "source":"ZaubaCorp", "source_url":f"https://www.zaubacorp.com/company/{quote_plus(cin)}"})
    df = pd.DataFrame(rows)
    df.to_csv(OUT_ENRICH, index=False)
    print("Saved enriched:", OUT_ENRICH)

if __name__ == "__main__":
    # read latest change log and sample top 80
    changes = pd.read_csv("outputs/change_logs/change_log_2025-10-03.csv")
    cins = changes['CIN'].unique()[:80].tolist()
    enrich_list(cins)
