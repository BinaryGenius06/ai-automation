# AI Automation Portfolio

Building production-grade AI automation tools for real-world business problems.
Each day = one focused build sprint.

---

## Stack
- Python 3.13
- Groq API (Llama 3.3-70b) — speed + volume
- Google Gemini (gemini-2.5-flash) — reasoning + quality
- python-dotenv, pdfplumber, langchain
- n8n self-hosted via Docker — visual workflow automation
- Docker Desktop
- ngrok — public URL for local webhooks
- Google Sheets API + OAuth2

---

## Structure

    ai-automation/
    ├── day-1/     → LLM API integration + data extraction pipeline
    ├── day-2/     → PDF to structured JSON extractor
    ├── day-3/     → n8n webhook to Google Sheets automation
    ├── workflows/ → exported n8n workflow JSONs
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
- Files: workflows/lead-capture-google-sheets.json\

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
- Files: telegram_bot/bot.py, telegram_bot/__init__.

### Day 9 — Telegram Bot: Groq Scoring + Sheets Logging + Hot Lead Alert
- Replaced 3x TODO markers with production logic: Groq scoring → Sheets logging → owner alert
- Built groq_scorer.py: standalone LLM classifier → hot/cold + reason + confidence
- Built sheets_logger.py: Google Sheets API (service account auth) → routes hot/cold to correct tab
- Wired both into bot.py: user ack sent first, Groq runs async, owner alerted instantly on hot leads
- Bot never crashes even if Groq or Sheets fails (try/except returns False, never raises)
- 4 test scenarios passed: hot lead, cold lead, borderline, Sheets failure resilience
- Stack: python-telegram-bot, Groq API, Google Sheets API, service account credentials

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

---

## Goal
Ship real AI tools. Build portfolio. Land clients or internships.