# AI Customer Support Bot — Any PDF → Instant Q&A Bot
## Live Demo
**[https://support-bot-wc7k.onrender.com](https://support-bot-wc7k.onrender.com)**

Try it — paste any PDF URL → ask questions instantly.

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
| KaTeX | LaTeX math rendering in chat UI |
| Render (free tier) | 24/7 hosting, no credit card |
| UptimeRobot | Pings /health every 5 min → no sleep |

## Setup (Local Dev)
```powershell
pip install fastapi uvicorn httpx pdfplumber python-dotenv aiofiles
python -m uvicorn support_bot.app:app --port 8000 --host 0.0.0.0
```
Load via local path: `{"pdf_path": "day-2/tutorial_groups.pdf"}`

## Setup (Production)
1. Deploy to Render → Start Command: `uvicorn support_bot.app:app --host 0.0.0.0 --port $PORT`
2. Set env var: `GROQ_API_KEY`
3. Get PDF URL from Google Drive:
   - Upload → Share → Anyone with link → copy link
   - Convert: `https://drive.google.com/uc?export=download&id=FILE_ID`
4. Paste URL in chat → Load → ask questions

## Endpoints
| Endpoint | Method | Purpose |
|---|---|---|
| /load | POST | Load PDF into knowledge base |
| /chat | POST | Ask a question |
| /reset | DELETE | Clear state |
| /status | GET | Check loaded doc + chunk count |
| /health | GET, HEAD | UptimeRobot health check |

## Common Errors
| Error | Fix |
|---|---|
| `groq` SDK hangs | Use `httpx` directly instead |
| `uvicorn` not binding | Use `python -m uvicorn` not just `uvicorn` |
| PDF not found | Run uvicorn from repo root, use relative path |
| StaticFiles error | `pip install aiofiles` |
| Google Drive URL returns HTML | Use `uc?export=download&id=FILE_ID` format. File must be shared publicly |
| `application/octet-stream` error | Already handled — allowed content type |
| UptimeRobot 405 on /health | Fixed — endpoint accepts GET + HEAD |
| PDF too large | 10MB limit enforced — use smaller PDF |

## Commercial Value
₹10,000 – ₹15,000 per client

"Give me any document. I'll have a bot answering questions about it in 10 minutes."

---
Built by [Suryansh Uttam](https://github.com/BinaryGenius06) — IIT Delhi