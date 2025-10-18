# src/ai_chatbot.py
def ask_mca_bot(query: str) -> str:
    """Dummy placeholder chatbot (so Streamlit won't break)."""
    if not query.strip():
        return "Please enter a question."
    return f"🤖 (Placeholder) You asked: '{query}'. The intelligent MCA Bot will answer this in the full version!"
