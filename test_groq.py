import httpx, os
from dotenv import load_dotenv
load_dotenv()

r = httpx.post(
    'https://api.groq.com/openai/v1/chat/completions',
    headers={
        'Authorization': f'Bearer {os.environ["GROQ_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'model': 'llama-3.3-70b-versatile',
        'messages': [{'role': 'user', 'content': 'say hi'}]
    },
    timeout=15
)
print(r.status_code, r.text[:200])