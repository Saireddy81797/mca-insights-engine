# src/change_detector.py
import pandas as pd
from pathlib import Path
from datetime import datetime

MASTER_DIR = Path("data/snapshots")
OUT_DIR = Path("outputs/change_logs")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_snapshot(date_suffix):
    # read all files with suffix date
    files = sorted(MASTER_DIR.glob(f"*_{date_suffix}.csv"))
    parts = []
    for f in files:
        df = pd.read_csv(f, dtype=str, low_memory=False)
        df['SOURCE_FILE'] = f.name
        parts.append(df)
    if not parts:
        return pd.DataFrame()
    snap = pd.concat(parts, ignore_index=True)
    snap['CIN'] = snap['CIN'].str.strip().str.upper()
    snap = snap.drop_duplicates(subset=['CIN'], keep='last')
    return snap

def diff_snapshots(old, new, date):
    # old/new are dataframes with same canonical columns
    changes = []
    old_idx = old.set_index('CIN')
    new_idx = new.set_index('CIN')

    old_cins = set(old_idx.index)
    new_cins = set(new_idx.index)

    added = new_cins - old_cins
    removed = old_cins - new_cins
    common = old_cins & new_cins

    for cin in added:
        row = new_idx.loc[cin].to_dict()
        changes.append({
            "CIN": cin, "Change_Type": "New Incorporation",
            "Field_Changed":"ALL", "Old_Value": None,
            "New_Value": str(row),
            "Date": date
        })
    for cin in removed:
        row = old_idx.loc[cin].to_dict()
        changes.append({
            "CIN": cin, "Change_Type": "Deregistered/Removed",
            "Field_Changed":"ALL", "Old_Value": str(row),
            "New_Value": None,
            "Date": date
        })
    # field level changes
    for cin in common:
        o = old_idx.loc[cin]
        n = new_idx.loc[cin]
        for col in ['COMPANY_NAME','AUTHORIZED_CAPITAL','PAIDUP_CAPITAL','STATUS','PRINCIPAL_BUSINESS_ACTIVITY','REGISTERED_OFFICE_ADDRESS']:
            ov = str(o.get(col, '') or '')
            nv = str(n.get(col, '') or '')
            if ov != nv:
                changes.append({
                    "CIN": cin, "Change_Type": "Field Update",
                    "Field_Changed": col, "Old_Value": ov, "New_Value": nv,
                    "Date": date
                })
    return pd.DataFrame(changes)

def run_for_dates(dates):  # dates list of suffix strings e.g. ['2025-10-01','2025-10-02']
    for i in range(1, len(dates)):
        old = load_snapshot(dates[i-1])
        new = load_snapshot(dates[i])
        date = dates[i]
        changes = diff_snapshots(old, new, date)
        out_csv = OUT_DIR / f"change_log_{date}.csv"
        changes.to_csv(out_csv, index=False)
        print("Wrote", out_csv)

if __name__ == "__main__":
    # example: three simulated days
    run_for_dates(["2025-10-01","2025-10-02","2025-10-03"])
