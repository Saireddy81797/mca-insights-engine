import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env for local development
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("⚠️ OpenAI API key not found! Please set it in .env or Streamlit Secrets.")

client = OpenAI(api_key=api_key)

def ask_mca_bot(question: str) -> str:
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for MCA insights."},
                {"role": "user", "content": question}
            ],
            max_tokens=200,
            temperature=0.4
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"
