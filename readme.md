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
├── day-2/ → PDF to structured JSON extractor
└── README.md

---

## Days

### Day 1 — LLM API Integration Sprint
- Connected Groq + Gemini APIs
- Built extract_structured() — extracts any schema from any text as JSON
- Files: groq_test.py, gemini_test.py, structured_output.py

### Day 2 — PDF → Structured Data Extractor
- Built pdf_extractor.py — extracts structured JSON from any text-based PDF
- Tested on resume, academic tutorial sheet, lecture notes
- Added error handling, JSON output saved to file
- Files: pdf_extractor.py, day2_explore.py, output_resume.json

---

## Model Selection Rule

| Use Case | Model |
|---|---|
| Extraction, classification, high volume | Groq (free, unlimited) |
| Complex reasoning, client-facing output | Gemini (1500/day) |

---

## Goal
Ship real AI tools. Build portfolio. Land clients or internships.