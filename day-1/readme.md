# AI Automation Portfolio

## Day 1 — LLM API Integration Sprint

### What I built
- Connected Groq API (Llama 3.3-70b) — fast, free LLM calls from Python
- Connected Gemini API (gemini-2.5-flash) — smarter reasoning model
- Built `extract_structured()` — reusable function that extracts any schema from any text as JSON

### Files
- `groq_test.py` — Groq API health check + basic LLM call
- `structured_output.py` — core data extraction pipeline (invoice + exam question test)
- `gemini_test.py` — Gemini API health check

### Stack
- Python 3.13
- groq 1.1.2
- google-genai
- python-dotenv
- pdfplumber

### Model selection rule
- Groq → speed, volume, extraction, classification, free, unlimited
- Gemini → complex reasoning, client-facing output, max 1500 calls/day

### Key concept learned
`extract_structured(any_text, any_schema)` → returns structured dict
Works on invoices, emails, resumes, exam questions, product listings.
Foundation of every automation built this month.