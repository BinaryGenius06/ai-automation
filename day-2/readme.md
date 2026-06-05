# Day 2 — PDF → Structured Data Extractor

## Overview

Day 2 was about solving one of the most common real-world automation problems: extracting structured data from unstructured PDF documents. Every business has PDFs — invoices, resumes, fee receipts, assignment sheets, application forms. They're all sitting in folders being manually read by humans.

The tool built today takes any text-based PDF, extracts all the text using pdfplumber, sends it to Groq with a schema description, and gets back clean structured JSON. One function call. Works on anything.

---

## Business Problem Being Solved

PDFs are everywhere but the data inside them is trapped:
- CA firms receive 200+ invoices per month → manually type data into spreadsheets
- Recruiters read resumes one by one → manually extract name, skills, experience
- Coaching institutes have PDF fee receipts → manually verify payments
- Universities have PDF assignment sheets → manually catalog questions

This tool automates all of that. Give it any PDF and a schema → get back structured data in under 10 seconds.

Commercial value:
- Resume parser for a recruiter → ₹5,000 - ₹8,000
- Invoice extractor for a CA firm → ₹8,000 - ₹12,000
- Academic document processor → ₹3,000 - ₹6,000

---

## Tech Stack

- Python 3.13
- pdfplumber → PDF text extraction
- Groq API (Llama 3.3-70b, free) → LLM inference for structured extraction
- python-dotenv → API key management

---

## Architecture

    PDF file (any text-based PDF)
        ↓
    pdfplumber (extract raw text, page by page)
        ↓
    Groq API (send text + schema → get JSON back)
        ↓
    json.loads (parse response string to Python dict)
        ↓
    save_result() (write to .json output file)

---

## File Structure

    day-2/
    ├── day2_explore.py      → explore raw pdfplumber output on any PDF
    ├── pdf_extractor.py     → main extraction pipeline
    └── README.md

---

## How It Works

### Step 1 — Extract raw text from PDF

pdfplumber opens the PDF page by page and extracts all text content. Works well on text-based PDFs (digitally created). Returns None or empty string for scanned/image PDFs.

```python
def extract_text_from_pdf(pdf_path: str) -> str:
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text.strip()
```

### Step 2 — Send to Groq with schema

The schema description is plain English. You tell Groq exactly what fields to extract and in what format. Temperature 0 makes it deterministic — same input always gives same output.

```python
def extract_structured(raw_text: str, schema_description: str) -> dict:
    if not raw_text:
        return {"error": "No text extracted from PDF"}

    if len(raw_text) > 6000:
        raw_text = raw_text[:6000] + "\n[truncated]"

    prompt = f"""Extract the following information from the text below.
Return ONLY valid JSON. No explanation. No markdown. No code blocks.

What to extract: {schema_description}

Text:
{raw_text}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        raw = response.choices[0].message.content.strip()

        if "```" in raw:
            parts = raw.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                try:
                    return json.loads(part)
                except:
                    continue

        return json.loads(raw)

    except json.JSONDecodeError as e:
        return {
            "error": "JSON parsing failed",
            "raw_response": raw,
            "detail": str(e)
        }
    except Exception as e:
        return {"error": str(e)}
```

### Step 3 — Main pipeline function

Combines both steps. This is the only function you need to call from outside.

```python
def process_pdf(pdf_path: str, schema_description: str) -> dict:
    print(f"Processing: {pdf_path}")
    raw_text = extract_text_from_pdf(pdf_path)

    if not raw_text:
        return {"error": "Could not extract text. PDF may be scanned/image-based."}

    print(f"Extracted {len(raw_text)} characters")
    return extract_structured(raw_text, schema_description)
```

### Step 4 — Save output to file

```python
def save_result(result: dict, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Saved to: {output_path}")
```

---

## Usage

```python
from pdf_extractor import process_pdf

# Resume
result = process_pdf(
    "resume.pdf",
    "name, email, phone, education (list of {degree, institution, year}), skills (list), projects (list of {title, tech_stack, description})"
)

# Invoice
result = process_pdf(
    "invoice.pdf",
    "invoice_number, date, vendor_name, client_name, line_items (list of {description, quantity, unit_price, total}), subtotal, tax, grand_total, due_date"
)

# Academic document
result = process_pdf(
    "tutorial.pdf",
    "course_code, topic, problems (list of {problem_number, description, subtasks (list)})"
)
```

Schema description controls output shape entirely. Be specific:

    bad  → "total"
    good → "total_amount_in_rupees"

---

## Tested On

### Resume (IIT Delhi student CV)
Extracted: name, email, phone, education, skills (17 items), projects (3 with tech stack and description)
Result: Clean JSON, all fields populated correctly

### Group Theory Tutorial Sheet (MTL2005)
Extracted: course code, topic, all 20 problems with subtasks
Result: Full problem set in structured JSON, each subtask as separate item

### Probability Theory Lecture Notes (6 pages)
Extracted: course name, topics covered, key theorems with formulas, recommended exercises
Result: Clean extraction, theorems with formulas preserved correctly

---

## Exploration Script

Before building the main extractor, use day2_explore.py to understand what pdfplumber returns for any PDF:

```python
import pdfplumber

PDF_PATH = r"your_file.pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    print(f"Total pages: {len(pdf.pages)}")

    for i, page in enumerate(pdf.pages):
        print(f"\n--- Page {i+1} ---")
        text = page.extract_text()
        print(text)

        tables = page.extract_tables()
        if tables:
            print(f"\nFound {len(tables)} table(s) on page {i+1}")
            for t in tables:
                print(t)
```

What to observe:
- Does extract_text() return clean text or garbage? → clean = text-based PDF → will work
- Returns None or empty → scanned/image PDF → pdfplumber won't work, need OCR
- Tables found → extract_tables() catches them separately

---

## Setup

Install dependencies:

    pip install groq pdfplumber python-dotenv

Add to .env file in root folder:

    GROQ_API_KEY=your_key_here

Run:

    python pdf_extractor.py

---

## Limitations

- Only works on text-based PDFs (digitally created)
- Scanned PDFs (photos of documents) return empty → need OCR (Day 10+ problem)
- Truncates at 6000 characters → long PDFs lose content from later pages
- Table extraction via pdfplumber can be inconsistent on complex layouts

---

## Bugs Hit and How They Were Fixed

**KeyError: GROQ_API_KEY**
.env file was in day-1 folder, not root folder.
Fix: Move .env to root folder. python-dotenv automatically searches parent directories.

**ModuleNotFoundError: groq**
Packages installed globally but venv was activated.
Fix: Deactivate venv → run python globally for this project.

**json.JSONDecodeError**
Model sometimes adds markdown backticks around JSON despite being told not to.
Fix: Strip markdown code blocks before json.loads using the split("```") logic.

**recommended_exercises empty in probability PDF**
6000 character truncation cut off the exercises section which was on later pages.
Fix: Increase truncation limit to 6000+ or process PDF in chunks for long documents.

---

## Key Concepts Learned

- pdfplumber extracts text page by page → concatenate for full document
- Temperature 0 = deterministic LLM output → essential for structured extraction
- Schema description is prompt engineering → be specific and explicit
- JSON parsing needs defensive coding → always handle markdown stripping
- extract_structured() is a universal primitive → works on any text, any schema
- Scanned PDFs are a different problem → pdfplumber only handles text-based

---

## The Core Insight

extract_structured(any_text, any_schema) → returns structured dict

This function is the foundation of every document automation pipeline. Change the schema description and it works on a completely different document type. No code changes needed. That's the power of LLM-based extraction over traditional regex or rule-based parsing.

---

## What This Is Worth

- Resume parser for a recruiting firm → ₹5,000 - ₹8,000
- Invoice extractor for a CA firm → ₹8,000 - ₹12,000
- Fee receipt processor for a coaching institute → ₹5,000 - ₹7,000
- Academic document cataloger → ₹3,000 - ₹6,000

---

## Next — Day 3
n8n setup via Docker. Build a webhook → Google Sheets pipeline. This is the visual automation layer that clients actually see and understand. Day 2 was the Python backend. Day 3 is the no-code frontend.