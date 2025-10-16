import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_mca_bot(question):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an MCA data assistant answering company-related questions."},
                {"role": "user", "content": question}
            ],
            max_tokens=200,
            temperature=0.4
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"
