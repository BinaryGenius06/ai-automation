import os, json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
def extract_structured(raw_text: str, schema_description: str) -> dict:
    """Takes raw text + schema. Returns dict."""
    prompt = f"""
    Extract the following information from the text below.
    Return ONLY valid JSON. No explanation. No markdown. No code blocks.

    What to extract: {schema_description}

    Text:
    {raw_text}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)
invoice_text = """
Invoice #1042
Date: 15 May 2026
Client: Rahul Sharma
Items: 2x Logo Design @ 3000, 1x Website Banner @ 1500
Total: 7500
Due: 30 May 2026
"""
result = extract_structured(
    invoice_text,
    "invoice_number, date, client_name, items (list of {name, quantity, price}), total, due_date"
)
print(json.dumps(result, indent=2, ensure_ascii=False))
exam_text = """
Let G be a group of order 35. Prove that G is cyclic.
Use Sylow theorems to show unique subgroups of order 5 and 7.
"""

result2 = extract_structured(
    exam_text,
    "topic, difficulty_level, concepts_tested (list)"
)

print(json.dumps(result2, indent=2, ensure_ascii=False))