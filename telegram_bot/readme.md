# Telegram Lead Qualification Bot — AI-powered lead qualifier for Indian SMBs

## Live Bot

**[@leadqual_suryansh_bot](https://t.me/leadqual_suryansh_bot)**

Try it — send `/start` and go through the flow.

Deployed on Render (free, always-on) + UptimeRobot monitoring.
Live server: https://ai-automation-zp9w.onrender.com

[▶ Watch Demo (Loom)](https://www.loom.com/share/e2e0f2f667b54e1da11559ffbd59d2a9)


---

## What It Does

Replaces manual WhatsApp/DM lead screening. Bot asks 4 questions → Groq LLM scores the lead → logs to Google Sheets → alerts owner instantly on hot leads. Zero human involvement until a hot lead is flagged.

---

## Demo Flow

```
User: /start
Bot:  What's your name?
User: Rahul Sharma
Bot:  What does your business do?
User: I run a coaching institute with 200 students
Bot:  What's your biggest challenge right now?
User: I spend 3 hours daily qualifying leads manually
Bot:  What's your email?
User: rahul@example.com
Bot:  Thanks! We'll be in touch shortly.

[Groq scores → HOT]
[Sheet row logged → Hot Leads tab]
[Owner alert → 🔥 HOT LEAD: Rahul Sharma...]
```

---

## Use Cases

- Coaching institutes → qualify 50+ daily inquiries automatically
- D2C brands → filter serious buyers from browsers
- Recruitment agencies → pre-screen candidates
- Any business getting leads via Telegram

---

## How It Works

```
User sends /start
        ↓
4-state ConversationHandler (python-telegram-bot)
  WAITING_NAME → WAITING_BUSINESS → WAITING_PROBLEM → WAITING_EMAIL
        ↓
groq_scorer.py → Groq API (Llama 3.3-70b)
  → score: hot / warm / cold
  → reason + confidence
        ↓
sheets_logger.py → Google Sheets API
  → hot   → Hot Leads tab
  → warm  → Warm Leads tab
  → cold  → Cold Leads tab
        ↓
If hot → Telegram alert to owner instantly
```

---

## Stack

| Tool | Why |
|---|---|
| python-telegram-bot 22.7 | ConversationHandler, webhook mode |
| Groq API (Llama 3.3-70b) | Fast, free, unlimited LLM scoring |
| Google Sheets API | Persistent lead storage, shareable |
| FastAPI + Uvicorn | Webhook server for production |
| Render (free tier) | 24/7 hosting, no credit card |
| UptimeRobot | Pings /health every 5 min → no sleep |

---

## Repo Structure

```
telegram_bot/
├── handlers.py        → all conversation handler functions + state constants
├── bot.py             → local polling dev runner (not deployed)
├── webhook_server.py  → FastAPI webhook server (deployed on Render)
├── groq_scorer.py     → Groq LLM lead scorer → hot/warm/cold + reason
├── sheets_logger.py   → Google Sheets API logger → routes to correct tab
└── __init__.py
```

---

## Google Sheets Structure

```
AI Automation Leads
├── Hot Leads  → name | email | business | problem | score | reason | timestamp
├── Warm Leads → same
└── Cold Leads → same
```

---

## Scoring Logic

```
HOT  → specific pain + budget signal + decision maker + urgency
WARM → vague pain or early stage or no budget signal
COLD → no pain, wrong fit, testing, or no email provided
```

---

## Setup (Local Dev)

**1. Clone repo**
```powershell
git clone https://github.com/BinaryGenius06/ai-automation
cd ai-automation
```

**2. Install packages**
```powershell
pip install python-telegram-bot==22.7 groq google-api-python-client google-auth python-dotenv fastapi uvicorn httpx
```

**3. Set up .env**
```
TELEGRAM_BOT_TOKEN=your_token_from_botfather
TELEGRAM_OWNER_CHAT_ID=your_chat_id
GROQ_API_KEY=your_groq_key
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
```

**4. Run locally (polling)**
```powershell
python telegram_bot/bot.py
```

---

## Setup (Production Deploy)

**1. Create Render account** → render.com → free, no card

**2. New Web Service → connect GitHub → select repo**

**3. Configure:**
```
Build Command : pip install -r requirements.txt
Start Command : uvicorn telegram_bot.webhook_server:api --host 0.0.0.0 --port $PORT
Instance Type : Free
```

**4. Set all env vars** (same as .env above + `WEBHOOK_URL=https://ai-automation-zp9w.onrender.com`)

**5. Deploy → copy live URL → set as WEBHOOK_URL**

**6. Add UptimeRobot monitor** → `https://ai-automation-zp9w.onrender.com/health` → every 5 min

---

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/webhook` | POST | Receives Telegram updates |
| `/health` | GET, HEAD | UptimeRobot health check |
| `/` | GET | Status check |

---

## Common Errors Fixed

| Error | Fix |
|---|---|
| `ModuleNotFoundError: telegram_bot` | Run from repo root, not from inside telegram_bot/ |
| `from groq_scorer import` fails on server | Use `from telegram_bot.groq_scorer import` |
| `409 Conflict` | Local bot.py polling running while webhook active → Ctrl+C local bot |
| `405 Method Not Allowed` on health | Use `@api.api_route("/health", methods=["GET","HEAD"])` |
| `WEBHOOK_URL` empty in getWebhookInfo | Env var missing or wrong format — must be `https://` |
| UptimeRobot shows Down | Change HTTP method to GET or fix endpoint to accept HEAD |
| `pywinpty` build error on Linux | Use clean requirements.txt — no Windows-only packages |

---

## Limitations

- Render free tier: 750 hrs/month compute (enough for 1 service)
- Groq free: unlimited but rate limited at high volume
- Google Sheets API: 300 writes/min (more than enough)
- Bot handles 1 conversation at a time per user (stateful)

---

Built by [Suryansh Uttam](https://github.com/BinaryGenius06) — IIT Delhi
Contact: binarygenius.leads@gmail.com