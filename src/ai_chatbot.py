import os
from dotenv import load_dotenv
from openai import OpenAI

# Load your .env file
load_dotenv()

# Get your API key from environment
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Function to get chatbot response
def ask_mca_bot(question):
    if not api_key:
        return "⚠️ OpenAI API key not found! Please check your .env file."
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an MCA data assistant who answers questions about Indian company data."},
                {"role": "user", "content": question}
            ],
            max_tokens=200,
            temperature=0.4
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"
