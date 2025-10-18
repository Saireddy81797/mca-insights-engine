# ================== streamlit_app.py ==================

import streamlit as st
import pandas as pd
from pathlib import Path
import sys, os

# 👇 Add this to ensure Streamlit finds your src folder (IMPORTANT)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ✅ Import chatbot function
from src.ai_chatbot import ask_mca_bot

# --- File Paths ---
MASTER = Path("data/processed/mca_master.csv")
CHANGE_DIR = Path("outputs/change_logs")
ENRICHED = Path("outputs/enriched/enriched_sample.csv")
SUMMARY_DIR = Path("outputs/summaries")

# --- Page Setup ---
st.set_page_config(page_title="MCA Insights Engine", layout="wide")
st.title("📊 MCA Insights Engine")

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["🧾 Data Overview", "🔄 Change Logs", "💡 Enriched Insights", "🤖 AI Chatbot"])

# ====================== TAB 1 — DATA OVERVIEW ======================
with tab1:
    st.header("📄 Company Master Dataset")

    if MASTER.exists():
        master = pd.read_csv(MASTER)
        st.sidebar.header("Filters")

        states = sorted(master["STATE"].dropna().unique())
        statuses = sorted(master["STATUS"].dropna().unique())

        state = st.sidebar.multiselect("State", states)
        status = st.sidebar.multiselect("Status", statuses)
        year = st.sidebar.selectbox("Year of Incorporation", [None] + sorted(
            pd.to_datetime(master["DATE_OF_INCORPORATION"], errors="coerce").dropna().dt.year.unique().tolist()))

        df = master.copy()
        if state:
            df = df[df["STATE"].isin(state)]
        if status:
            df = df[df["STATUS"].isin(status)]
        if year:
            df = df[pd.to_datetime(df["DATE_OF_INCORPORATION"], errors="coerce").dt.year == int(year)]

        st.write(f"### Result count: {len(df)}")
        st.dataframe(df[["CIN", "COMPANY_NAME", "STATE", "STATUS", "AUTHORIZED_CAPITAL"]].head(200), use_container_width=True)

    else:
        st.warning("⚠️ Master file not found. Please upload `data/processed/mca_master.csv`.")

# ====================== TAB 2 — CHANGE LOGS ======================
with tab2:
    st.header("📅 Daily Change Logs")

    if CHANGE_DIR.exists():
        files = sorted(CHANGE_DIR.glob("*.csv"))
        if files:
            sel = st.selectbox("Select change log file", [f.name for f in files])
            if sel:
                changes = pd.read_csv(CHANGE_DIR / sel)
                st.metric("New Incorporations", (changes["Change_Type"] == "New Incorporation").sum())
                st.metric("Deregistered", (changes["Change_Type"] == "Deregistered/Removed").sum())
                st.metric("Field Updates", (changes["Change_Type"] == "Field Update").sum())
                st.dataframe(changes.head(200), use_container_width=True)
        else:
            st.info("No change logs found in `outputs/change_logs/`.")
    else:
        st.warning("⚠️ `outputs/change_logs/` folder missing!")

# ====================== TAB 3 — ENRICHED INSIGHTS ======================
with tab3:
    st.header("💡 Enriched Company Details")

    if ENRICHED.exists():
        en = pd.read_csv(ENRICHED)
        cin = st.text_input("Enter CIN to look up company details")

        if cin:
            record = en[en["CIN"].str.upper() == cin.strip().upper()]
            if not record.empty:
                st.success(f"✅ Found record for {cin}")
                st.json(record.iloc[0].to_dict())
            else:
                st.warning("No company found with that CIN in enriched dataset.")
        else:
            st.dataframe(en.head(15), use_container_width=True)
    else:
        st.warning("⚠️ Enriched sample file not found. Please upload `outputs/enriched/enriched_sample.csv`.")

# ====================== TAB 4 — AI CHATBOT ======================
with tab4:
    st.header("🤖 MCA AI Chatbot")

    st.write("Ask any question related to MCA company data (for example: *Show me companies registered in Maharashtra in 2024*).")

    user_question = st.text_input("💬 Type your question:")

    if st.button("Ask"):
        if not user_question.strip():
            st.warning("⚠️ Please enter a question first.")
        else:
            with st.spinner("Thinking... 🤔"):
                answer = ask_mca_bot(user_question)
            st.success("✅ Chatbot Response:")
            st.write(answer)
