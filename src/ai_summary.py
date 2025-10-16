# src/ai_summary.py
import pandas as pd
import json
from pathlib import Path

IN = Path("outputs/change_logs/change_log_2025-10-03.csv")
OUT = Path("outputs/summaries/daily_summary_2025-10-03.json")
OUT.parent.mkdir(parents=True, exist_ok=True)

def generate_summary(df):
    total_new = (df['Change_Type']=="New Incorporation").sum()
    total_removed = (df['Change_Type']=="Deregistered/Removed").sum()
    total_updates = (df['Change_Type']=="Field Update").sum()
    # top fields changed
    top_fields = df[df['Field_Changed'] != 'ALL']['Field_Changed'].value_counts().to_dict()
    # example notable transitions (status)
    status_changes = df[df['Field_Changed']=="STATUS"].head(10).to_dict(orient='records')
    summary = {
        "date": IN.stem.split("_")[-1],
        "new_incorporations": int(total_new),
        "deregistered": int(total_removed),
        "updated_records": int(total_updates),
        "top_fields_changed": top_fields,
        "sample_status_changes": status_changes
    }
    return summary

if __name__ == "__main__":
    df = pd.read_csv(IN)
    s = generate_summary(df)
    OUT.write_text(json.dumps(s, indent=2))
    print("Wrote", OUT)
