import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What are the top 3 use cases for AI automation in small businesses?"}
    ]
)
print(response.choices[0].message.content)
print(f"\nTokens used: {response.usage.total_tokens}")