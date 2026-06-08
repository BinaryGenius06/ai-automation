# AI Customer Support Bot — Any PDF → Instant Q&A Bot

Answers questions about any document using Groq (Llama 3.3-70b).
Keyword-based retrieval — no vector DB, no paid embeddings, no setup.

## Use Cases
- Coaching institute FAQ (fees, syllabus, schedule)
- Product manual Q&A for D2C brands
- Policy/HR document assistant
- Course material bot for EdTech

## How It Works
PDF → chunk (400 char) → keyword search → top 3 chunks → Groq → answer

Escalates to human if answer not in document — never hallucinates.

## Stack
| Tool | Why |
|---|---|
| pdfplumber | PDF text extraction |
| Groq (Llama 3.3-70b) | Fast, free LLM |
| FastAPI | /load, /chat, /reset, /status endpoints |
| Vanilla HTML/JS | Zero-dependency chat UI |

## Setup
```
pip install fastapi uvicorn groq pdfplumber python-dotenv aiofiles httpx
python -m uvicorn support_bot.app:app --port 8000 --host 0.0.0.0
```

## Endpoints
| Endpoint | Method | Purpose |
|---|---|---|
| /load | POST | Load PDF into knowledge base |
| /chat | POST | Ask a question |
| /reset | DELETE | Clear state |
| /status | GET | Check loaded doc + chunk count |

## Common Errors
| Error | Fix |
|---|---|
| `groq` SDK hangs | Use `httpx` directly instead |
| `uvicorn` not binding | Use `python -m uvicorn` not just `uvicorn` |
| PDF not found | Run uvicorn from repo root, use relative path |
| StaticFiles error | `pip install aiofiles` |

## Commercial Value
₹10,000 – ₹15,000 per client

"Give me any document. I'll have a bot answering questions about it in 10 minutes."

---
Built by [Suryansh Uttam](https://github.com/BinaryGenius06) — IIT Delhi