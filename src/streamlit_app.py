# src/streamlit_app.py
import streamlit as st
import pandas as pd
from pathlib import Path

MASTER = Path("data/processed/mca_master.csv")
ENRICHED = Path("outputs/enriched/enriched_sample.csv")
CHANGE_DIR = Path("outputs/change_logs")

st.set_page_config(page_title="MCA Insights Engine", layout="wide")

st.title("MCA Insights Engine — Dashboard")

master = pd.read_csv(MASTER)
st.sidebar.header("Filters")
state = st.sidebar.multiselect("State", options=sorted(master['STATE'].dropna().unique().tolist()))
year = st.sidebar.selectbox("Year", options=[None]+sorted(pd.to_datetime(master['DATE_OF_INCORPORATION'], errors='coerce').dropna().dt.year.unique().tolist()))
status = st.sidebar.multiselect("Status", options=sorted(master['STATUS'].dropna().unique().tolist()))

df = master.copy()
if state:
    df = df[df['STATE'].isin(state)]
if status:
    df = df[df['STATUS'].isin(status)]
if year:
    df = df[pd.to_datetime(df['DATE_OF_INCORPORATION'], errors='coerce').dt.year == int(year)]

st.write("Result count:", len(df))
st.dataframe(df[['CIN','COMPANY_NAME','STATE','STATUS','AUTHORIZED_CAPITAL']].head(200))

# change history visualization (simple counts)
st.subheader("Daily change logs")
files = sorted(CHANGE_DIR.glob("change_log_*.csv"))
sel = st.selectbox("Select change log", [f.name for f in files])
if sel:
    changes = pd.read_csv(CHANGE_DIR / sel)
    st.write("New incorporations:", (changes['Change_Type']=="New Incorporation").sum())
    st.write("Deregistered:", (changes['Change_Type']=="Deregistered/Removed").sum())
    st.write("Field updates:", (changes['Change_Type']=="Field Update").sum())
    st.dataframe(changes.head(200))

# Enriched company viewer
st.subheader("Enriched company details")
en = pd.read_csv(ENRICHED)
cin = st.text_input("Enter CIN to lookup")
if cin:
    rec = en[en['CIN'].str.upper() == cin.strip().upper()]
    if not rec.empty:
        st.json(rec.iloc[0].to_dict())
    else:
        st.warning("Not found in enriched sample")
