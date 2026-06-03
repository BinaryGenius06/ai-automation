# PDF → Structured Data Extractor

Extracts structured JSON from any text-based PDF using Groq (free LLM API).

## Use Cases
- Resume parsing for recruiters
- Invoice data extraction for CA firms
- Academic document processing

## Setup
pip install groq pdfplumber python-dotenv
Add GROQ_API_KEY to .env

## Usage
from pdf_extractor import process_pdf
result = process_pdf("your_file.pdf", "name, email, skills (list)")

## Stack
- Groq API (free) — LLM inference
- pdfplumber — PDF text extraction
- Python 3.13