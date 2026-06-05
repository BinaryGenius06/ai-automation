# Day 1 — LLM API Integration Sprint

## Overview

Day 1 was about getting the foundation right. Before building any automation, you need to be able to talk to an LLM from code. That sounds simple but there are real decisions to make: which model, which API, how to handle responses, how to get structured data back reliably.

By end of Day 1, two APIs were connected (Groq + Gemini), and one reusable function was built that became the backbone of everything built after it: extract_structured(). Give it any text and any schema description, get back a Python dict. That's it. That's the primitive everything else plugs into.

---

## Business Problem Being Solved

Raw text is everywhere — invoices, emails, resumes, forms, exam papers. The data inside is valuable but trapped in an unstructured format. Extracting it manually is slow and expensive.

extract_structured() solves this universally. One function, any document type, any schema. This is the core building block of document automation, data pipelines, and AI-powered processing tools.

---

## Tech Stack

- Python 3.13
- Groq API (Llama 3.3-70b-versatile, free, unlimited) → speed + volume
- Google Gemini API (gemini-2.5-flash, free, 1500/day) → reasoning + quality
- python-dotenv → API key management from .env file
- pdfplumber → PDF text extraction (used from Day 2 onwards)

---

## Architecture

    Raw text (invoice, resume, exam question, anything)
        +
    Schema description (plain English: "name, email, skills (list)")
        ↓
    extract_structured()
        ↓
    Groq API (Llama 3.3-70b, temperature=0)
        ↓
    JSON string → json.loads() → Python dict

---

## File Structure

    day-1/
    ├── groq_test.py          → Groq API health check + basic LLM call
    ├── structured_output.py  → core data extraction pipeline
    ├── gemini_test.py        → Gemini API health check
    └── README.md

---

## Setup

Install dependencies:

    pip install groq google-generativeai python-dotenv pdfplumber

Create .env file in root folder:

    GROQ_API_KEY=your_groq_key_here
    GEMINI_API_KEY=your_gemini_key_here

Get Groq API key → console.groq.com → API Keys → Create Key (free, no card)
Get Gemini API key → aistudio.google.com → Get API Key (free, no card)

---

## How It Works

### Basic Groq Call

```python
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 17 * 23? Show your working."}
    ]
)

print(response.choices[0].message.content)
print(f"\nTokens used: {response.usage.total_tokens}")
```

Response path to memorize:

    response → .choices[0] → .message → .content = your text
    response → .usage → .total_tokens = token count

### extract_structured() — The Core Primitive

```python
import os, json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])

def extract_structured(raw_text: str, schema_description: str) -> dict:
    """Takes raw text + schema description. Returns Python dict."""
    prompt = f"""Extract the following information from the text below.
Return ONLY valid JSON. No explanation. No markdown. No code blocks.

What to extract: {schema_description}

Text:
{raw_text}"""

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
```

Why temperature=0: deterministic output. Same input always gives same structure back. Essential for extraction tasks where consistency matters.

Why markdown stripping: even with explicit instructions, LLMs sometimes wrap JSON in backticks. Defensive coding handles this silently.

### Basic Gemini Call

```python
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain what n8n is in 3 sentences, for a developer who knows Python."
)

print(response.text)
```

Note: Use google.genai not google.generativeai — the old package is deprecated.

---

## Tested On

### Invoice Text
Input: fake invoice with vendor, client, line items, total, due date
Schema: "invoice_number, date, client_name, items (list of {name, quantity, price}), total, due_date"
Result: Clean JSON with all fields populated including nested items list

### Exam Question (Abstract Algebra)
Input: Group theory problem about cyclic groups and Sylow theorems
Schema: "topic, difficulty_level, concepts_tested (list)"
Result: topic: Group Theory, difficulty: Advanced, concepts: [Sylow Theorems, Cyclic Groups, Order of a Group]

---

## Model Selection Rule

| Use Case | Model |
|---|---|
| Extraction, classification, high volume tasks | Groq (free, unlimited) |
| Complex reasoning, client-facing responses | Gemini Flash (1500/day free) |

Rule of thumb:
- Default to Groq → fast (under 1 second), free, handles 99% of tasks
- Upgrade to Gemini → when output quality visibly matters to the end user

Speed comparison observed:
- Groq → ~500ms response on 70B model
- Gemini Flash → 2-4 seconds, slightly richer output

---

## Bugs Hit and How They Were Fixed

**venv creation failing with KeyboardInterrupt**
ensurepip was trying to download pip and hung on slow/blocked network.
Fix: python -m venv venv --without-pip → then python -m ensurepip --upgrade separately. Or skip venv entirely and install globally for solo projects.

**FutureWarning on google.generativeai**
Old Gemini SDK deprecated. All support ended.
Fix: Switch to google.genai package. Import and usage syntax changes slightly.

**ModuleNotFoundError after venv activation**
Packages were installed globally but venv was activated — venv has its own isolated packages.
Fix: Deactivate venv → run python globally. For this project venv is optional.

**json.JSONDecodeError on Groq response**
Model added backtick markdown despite instructions not to.
Fix: Add markdown stripping logic before json.loads. Add print(raw) for debugging when this happens.

---

## Key Concepts Learned

- API call structure: model + messages (system + user roles) + temperature
- temperature=0 → deterministic → use for extraction, classification, structured tasks
- temperature>0 → creative → use for writing, replies, brainstorming
- Response path: response.choices[0].message.content = the text
- Markdown stripping = defensive coding for LLM outputs
- python-dotenv loads .env from current or parent directory automatically
- Groq free tier has no daily limit → use it for everything high-volume

---

## The Core Insight

    extract_structured(any_text, any_schema) → returns structured dict

This is not just a utility function. It is the universal primitive for document intelligence. Every automation that processes documents — invoices, resumes, emails, forms — uses exactly this pattern underneath.

Change the schema description and it handles a completely different document type. No retraining, no fine-tuning, no regex. Just prompt engineering.

---

## What This Is Worth

A developer who can reliably extract structured data from any document using LLMs can:
- Build document automation tools for CA firms, recruiters, coaching institutes
- Integrate into larger pipelines (n8n, Make, custom APIs)
- Charge ₹3,000 - ₹12,000 per tool depending on complexity

Day 1 built the core of all of that.

---

## Next — Day 2
pdfplumber + Groq together. Take any PDF file → extract text → run extract_structured() → get clean JSON. Test on a real resume, a tutorial sheet, and a lecture notes PDF. Build error handling and file output.