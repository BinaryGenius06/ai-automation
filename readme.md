# AI Automation Portfolio

Building production-grade AI automation tools for real-world business problems.
Each day = one focused build sprint.

---

## Stack
- Python 3.13
- Groq API (Llama 3.3-70b) — speed + volume
- Google Gemini (gemini-2.5-flash) — reasoning + quality
- python-dotenv, pdfplumber, langchain

---

## Structure

ai-automation/
├── day-1/ → LLM API integration + data extraction pipeline
├── day-2/ → coming soon
└── README.md

---

## Days

### Day 1 — LLM API Integration Sprint
- Connected Groq + Gemini APIs
- Built extract_structured() — extracts any schema from any text as JSON
- Files: groq_test.py, gemini_test.py, structured_output.py

---

## Model Selection Rule

| Use Case | Model |
|---|---|
| Extraction, classification, high volume | Groq (free, unlimited) |
| Complex reasoning, client-facing output | Gemini (1500/day) |

---

## Goal
Ship real AI tools. Build portfolio. Land clients or internships.