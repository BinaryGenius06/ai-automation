# AI Automation Portfolio

Building production-grade AI automation tools for real-world business problems.
Each day = one focused build sprint.

---

## Live Projects

| Project | What it does | Stack | Live | Demo |
|---|---|---|---|---|
| [Telegram Lead Bot](telegram_bot/) | Qualifies leads hot/cold via AI, alerts owner on hot leads | python-telegram-bot · Groq · Google Sheets · FastAPI | [t.me/leadqual_suryansh_bot](https://t.me/leadqual_suryansh_bot) | [▶ Watch](https://www.loom.com/share/e2e0f2f667b54e1da11559ffbd59d2a9) |
| [AI Support Bot](support_bot/) | Answers customer questions from any PDF or URL | FastAPI · Groq · pdfplumber · KaTeX | [support-bot-wc7k.onrender.com](https://support-bot-wc7k.onrender.com) | [▶ Watch](https://www.loom.com/share/07e5c4e13c014f2fae4c7e65d30b23e1) |


## Stack
- Python 3.13
- Groq API (Llama 3.3-70b) — speed + volume
- Google Gemini (gemini-2.5-flash) — reasoning + quality
- python-dotenv, pdfplumber, httpx, aiofiles
- FastAPI + Uvicorn — API backend
- python-telegram-bot 22.7 — Telegram bot framework
- n8n self-hosted via Docker — visual workflow automation
- Docker Desktop
- ngrok — public URL for local webhooks
- Google Sheets API + OAuth2
- Render — free cloud deployment (no card)
- UptimeRobot — uptime monitoring
- KaTeX — LaTeX math rendering in chat UI

---

## Structure

    ai-automation/
    ├── day-1/         → LLM API integration
    ├── day-2/         → PDF to structured JSON extractor
    ├── day-3/         → n8n webhook to Google Sheets
    ├── day-4/         → AI lead qualifier (Gmail + Groq)
    ├── day-5/         → Make.com survey
    ├── telegram_bot/  → AI lead qualification bot (LIVE)
    ├── support_bot/   → AI customer support bot (LIVE)
    ├── workflows/     → exported n8n + Make workflow JSONs
    ├── Procfile       → Render deployment config
    ├── runtime.txt    → Python version pin
    └── README.md

---

## Days

### Day 1 — LLM API Integration Sprint
- Connected Groq + Gemini APIs
- Built extract_structured() — extracts any schema from any text as JSON
- Files: groq_test.py, gemini_test.py, structured_output.py

### Day 2 — PDF to Structured Data Extractor
- Built pdf_extractor.py — extracts structured JSON from any text-based PDF
- Tested on resume, academic tutorial sheet, lecture notes
- Added error handling, JSON output saved to file
- Files: pdf_extractor.py, day2_explore.py

### Day 3 — n8n Webhook to Google Sheets Automation
- n8n running locally via Docker
- Built webhook → Edit Fields → Google Sheets pipeline
- ngrok public URL for live demos
- Files: workflows/lead-capture-google-sheets.json

### Day 4 — AI Lead Qualifier (Gmail Trigger + Groq Scoring)
- Gmail Trigger → reads emails sent to binarygenius.leads@gmail.com
- Groq classifies leads → hot / warm / cold (3-tier scoring)
- Hot leads → Hot Leads sheet + alert to suryansh2020 + personalized auto-reply to sender
- Warm leads → Warm Leads sheet
- Cold leads → Cold Leads sheet
- Files: workflows/lead-qualifier-gmail-trigger.json

### Day 5 — Make.com Survey
- Recreated Day 3 webhook → Sheets in Make
- Groq called via HTTP module inside Make
- Built n8n vs Make decision framework
- **Stack:** Make.com, Google Sheets API, Groq API

### Day 6 — Market Research + Outreach Prep
- Built 20-target Notion outreach tracker (EdTech, D2C, Recruitment sectors)
- Each target has specific pain signal, founder name, contact channel
- 2 outreach templates written (warm + cold) saved to Notion
- Tools: Notion, LinkedIn, Instagram, web research

### Day 7 — GitHub Portfolio Polish
- Rewrote day-2 + day-4 READMEs as product pages (problem first, demo, use cases)
- Added workflow screenshot + demo output screenshot as assets
- Added docstrings to all functions, created .env.example
- Polished GitHub profile: bio, pinned repos, ecommerce-support-agent README
- Week 1 retrospective written in Notion

### Day 8 — Telegram Lead Bot: Architecture + Skeleton
- Designed 4-state conversation flow: WAITING_NAME → WAITING_BUSINESS → WAITING_PROBLEM → WAITING_EMAIL
- Built full bot skeleton using python-telegram-bot ConversationHandler
- All edge cases handled: /restart, short name, photo rejection, /start mid-flow
- 3x TODO Day 9 markers placed for Groq + Sheets + alert integration
- Files: telegram_bot/bot.py, telegram_bot/__init__.py

### Day 9 — Telegram Bot: Groq Scoring + Sheets Logging + Hot Lead Alert
- Replaced 3x TODO markers with production logic: Groq scoring → Sheets logging → owner alert
- Built groq_scorer.py: standalone LLM classifier → hot/cold + reason + confidence
- Built sheets_logger.py: Google Sheets API (service account auth) → routes hot/cold to correct tab
- Wired both into bot.py: user ack sent first, Groq runs async, owner alerted instantly on hot leads
- Bot never crashes even if Groq or Sheets fails (try/except returns False, never raises)
- 4 test scenarios passed: hot lead, cold lead, borderline, Sheets failure resilience
- Stack: python-telegram-bot, Groq API, Google Sheets API, service account credentials

### Day 10 — Telegram Bot: Production Deploy (Render + Webhook Mode)
- Refactored bot.py → handlers.py (importable module) + new bot.py (local polling dev)
- Built webhook_server.py: FastAPI + Uvicorn → receives Telegram updates via HTTPS POST
- Switched polling → webhook mode: Telegram pushes updates instantly, zero idle requests
- Deployed to Render (free tier, no card) → live 24/7 at https://ai-automation-zp9w.onrender.com
- Added UptimeRobot monitor → pings /health every 5 min → Render never sleeps
- Fixed clean requirements.txt → removed Windows-only packages (pywinpty etc.) for Linux server
- Verified: getWebhookInfo → correct URL, full end-to-end test passed in production
- Files: telegram_bot/handlers.py, telegram_bot/webhook_server.py, Procfile, runtime.txt, requirements.txt

### Day 11 — AI Customer Support Bot: PDF Knowledge Base + Chat UI
- Built knowledge_base.py: PDF loader (pdfplumber) → chunker (400 char + overlap) → keyword search
- Built app.py: FastAPI backend → /load, /chat, /reset, /status endpoints
- Conversation memory: last 4 exchanges preserved per session
- Escalation detection: bot flags "I don't know" answers → never hallucinates silently
- Built clean chat UI (vanilla HTML/CSS/JS) → KaTeX LaTeX rendering for math PDFs
- Fixed groq SDK hanging on Windows → replaced with direct httpx calls to Groq API
- Tested via ngrok public URL → works on phone, loads any PDF, answers in real time
- Stack: pdfplumber, Groq (Llama 3.3-70b via httpx), FastAPI, KaTeX, ngrok
- Files: support_bot/knowledge_base.py, support_bot/app.py, support_bot/static/index.html

### Day 12 — Support Bot: Production Deploy
- Added URL-based PDF loading → works on any server (no local file needed)
- Added SSRF protection → blocks private/internal URLs
- Added 10MB file size limit → protects free tier compute
- Added /health endpoint → UptimeRobot monitoring
- Deployed to Render (free tier, always-on via UptimeRobot)
- window.location.origin → UI works on localhost and production automatically
- Live: https://support-bot-wc7k.onrender.com
- Files: support_bot/knowledge_base.py, support_bot/app.py, support_bot/static/index.html

### Day 13 — LinkedIn Overhaul + GitHub Profile + Deployment Verification
- Created GitHub profile README (BinaryGenius06/BinaryGenius06) — live projects table, stack, contact
- Pinned ai-automation + ecommerce-support-agent repos on GitHub profile
- Added Loom demo links to telegram_bot/README.md and support_bot/README.md
- Verified all live deployments: Telegram bot ✅ · Support bot ✅ · UptimeRobot monitors green ✅
- Confirmed .env in .gitignore, no secrets in repo ✅
- Outreach pipeline expanded: 19 → 39 targets in Notion (EdTech, D2C, Recruitment)
- Days 1–12 audit completed in Notion — no real gaps going into Week 3
- LinkedIn new account submitted for manual review (pending 2–5 days)
- Outreach readiness: 2 live URLs ✅ · 2 Looms ✅ · 39 targets ✅ · 2 templates ✅

### Day 14 — Outreach CRM + Templates + Pre-Week 3 Prep
- Upgraded Notion Outreach Pipeline into a working CRM: added Follow-up Date, Reply Received, Call Booked, Project Value, Priority, Loom Sent + "Days Since Sent" formula
- Created 4 database views: This Week, Hot Pipeline, Follow-ups Due, All Contacts
- Assigned Priority (High/Medium/Low) across all 39 targets
- Wrote Template 3 (IIT Peer Warm) — third outreach template alongside Cold + Warm from Day 6
- Drafted 2 fully personalised IIT-warm messages, ready to send Day 15
- Documented outreach funnel math (30 → 6 → 3 → 2 → 1 → 0.5) + follow-up rule (Day 0/3/7/8)
- Built Discovery Call Script — 25-min structure + 5 sector-specific diagnose questions
- Verified both Loom demo links resolve correctly
- Outreach readiness: CRM live ✅ · 3 templates ✅ · 2 personalised drafts ✅ · funnel math understood ✅ · call script ready ✅

---

## Model Selection Rule

| Use Case | Model |
|---|---|
| Extraction, classification, high volume | Groq (free, unlimited) |
| Complex reasoning, client-facing output | Gemini (1500/day) |

---

## Cost
Everything is 100% free:
- Groq API → free, unlimited
- Gemini API → free, 1500/day
- n8n self-hosted → free
- Docker → free
- ngrok free tier → free
- Google Sheets API → free
- GitHub → free
- Render → free tier, no credit card
- UptimeRobot → free, 50 monitors

---

## Goal
Ship real AI tools. Build portfolio. Land clients or internships.
