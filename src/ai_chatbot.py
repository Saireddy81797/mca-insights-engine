import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables (for local or Streamlit Secrets)
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load MCA data (you can adjust path if needed)
DATA_PATH = "data/processed/mca_master.csv"

def ask_mca_bot(query: str) -> str:
    """
    Answers user questions about MCA company data.
    Combines simple pandas filtering with OpenAI summarization.
    """
    if not query.strip():
        return "Please enter a valid question."

    try:
        df = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        return "⚠️ MCA master data file not found. Please upload `data/processed/mca_master.csv`."

    # --- Simple rule-based query detection ---
    query_lower = query.lower()
    results = None

    if "telangana" in query_lower:
        results = df[df["STATE"].str.lower() == "telangana"]
    elif "maharashtra" in query_lower:
        results = df[df["STATE"].str.lower() == "maharashtra"]
    elif "karnataka" in query_lower:
        results = df[df["STATE"].str.lower() == "karnataka"]
    elif "tamil nadu" in query_lower or "tamilnadu" in query_lower:
        results = df[df["STATE"].str.lower().str.contains("tamil")]
    elif "delhi" in query_lower:
        results = df[df["STATE"].str.lower() == "delhi"]
    elif "active" in query_lower:
        results = df[df["STATUS"].str.lower() == "active"]
    elif "strike off" in query_lower:
        results = df[df["STATUS"].str.lower().str.contains("strike")]
    else:
        # fallback: give AI the summary directly
        context = df.head(15).to_dict(orient="records")
        prompt = f"You are an MCA assistant. The user asked: {query}\nHere is sample MCA data:\n{context}\nProvide a short, helpful answer."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a helpful assistant for MCA insights."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    if results is None or results.empty:
        return "No matching companies found for your query."

    # --- Summarize results using GPT ---
    sample = results.head(10).to_dict(orient="records")
    prompt = f"Summarize the following MCA company data based on this question: {query}\n\n{sample}\n\nGive a concise answer."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a helpful assistant for analyzing MCA company datasets."},
                  {"role": "user", "content": prompt}]
    )
    summary = response.choices[0].message.content

    # --- Display first few results + AI summary ---
    text = f"**Top {len(sample)} Matching Companies:**\n"
    for _, row in results.head(5).iterrows():
        text += f"- {row['COMPANY_NAME']} ({row['STATE']}, {row['STATUS']})\n"

    return f"{text}\n\n**AI Summary:**\n{summary}"
