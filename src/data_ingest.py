# src/data_ingest.py
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/snapshots")
OUT = Path("data/processed/mca_master.csv")

# expected canonical columns
COLUMNS = ["CIN","COMPANY_NAME","CLASS","DATE_OF_INCORPORATION",
           "AUTHORIZED_CAPITAL","PAIDUP_CAPITAL","STATUS","PRINCIPAL_BUSINESS_ACTIVITY",
           "REGISTERED_OFFICE_ADDRESS","ROC_CODE","STATE","SOURCE_FILE","SCRAPE_DATE"]

def normalize(df, source_file, state):
    # rename common variations to canonical
    rename_map = {
        "Company Name":"COMPANY_NAME","Name":"COMPANY_NAME",
        "CIN":"CIN","Cin":"CIN",
        "Date of Incorporation":"DATE_OF_INCORPORATION",
        "Authorized Capital":"AUTHORIZED_CAPITAL",
        "Paid up capital":"PAIDUP_CAPITAL",
        "Company Status":"STATUS",
        "Principle Business Activity":"PRINCIPAL_BUSINESS_ACTIVITY",
        "Registered Office Address":"REGISTERED_OFFICE_ADDRESS",
        "ROC Code":"ROC_CODE"
    }
    df = df.rename(columns=rename_map)
    # keep only columns in COLUMNS, fill missing
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = pd.NA
    df = df[COLUMNS]
    df["STATE"] = state
    df["SOURCE_FILE"] = source_file
    return df

def build_master():
    files = sorted(RAW_DIR.glob("*.csv"))
    parts = []
    for f in files:
        # derive state from filename convention: e.g., maharashtra_2025-10-01.csv
        state = f.name.split("_")[0].capitalize()
        df = pd.read_csv(f, dtype=str, low_memory=False)
        df = normalize(df, f.name, state)
        parts.append(df)
    master = pd.concat(parts, ignore_index=True)
    # standard cleaning
    master["CIN"] = master["CIN"].str.strip().str.upper()
    master = master.drop_duplicates(subset=["CIN"], keep="last")
    master.to_csv(OUT, index=False)
    print("Saved master:", OUT)

if __name__ == "__main__":
    build_master()
