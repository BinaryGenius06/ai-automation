# Day 3 — n8n Webhook → Google Sheets Automation

## What We Built
A live automation pipeline:
1. Receives data via webhook (HTTP POST)
2. Cleans and structures the data
3. Appends it as a new row in Google Sheets
4. Exposed via public URL using ngrok

---

## Why This Matters
Every client automation follows this exact pattern:
- Something happens (form submit, button click) → triggers webhook
- Data gets cleaned → Edit Fields node
- Data gets stored → Google Sheets, database, CRM

Master this pattern → build 80% of client automations.

---

## Stack
- n8n self-hosted via Docker
- Docker Desktop
- ngrok free tier
- Google Sheets API + OAuth2
- Google Cloud Console

---

## Workflow Architecture

    Webhook (POST /lead-capture)
        ↓
    Edit Fields (flatten + add timestamp)
        ↓
    Google Sheets (Append Row)

---

## Node Configuration

### Webhook Node
- Method: POST
- Path: lead-capture
- Response: Immediate 200

### Edit Fields Node

| Field | Expression |
|---|---|
| name | {{ $json.body.name }} |
| email | {{ $json.body.email }} |
| interest | {{ $json.body.interest }} |
| timestamp | {{ new Date().toISOString() }} |

### Google Sheets Node
- Operation: Append Row
- Sheet: AI Automation Leads
- Maps each field to column

---

## How to Run

### Start n8n
    docker start n8n

Open browser → http://localhost:5678

### Start ngrok
    ngrok http 5678

### Test locally
    Invoke-WebRequest -Uri "http://localhost:5678/webhook/lead-capture" -Method POST -ContentType "application/json" -Body '{"name": "Test User", "email": "test@example.com", "interest": "automation"}'

### Test via public URL
    Invoke-WebRequest -Uri "https://YOUR_NGROK_URL/webhook/lead-capture" -Method POST -ContentType "application/json" -Body '{"name": "Mobile Test", "email": "m@test.com", "interest": "test"}'

---

## Key Concepts Learned
- Webhook = URL that listens for HTTP requests → triggers automation
- Edit Fields node = transforms data between nodes
- Expressions use {{ }} syntax → {{ $json.fieldName }}
- OAuth2 = secure way to connect n8n to Google without sharing password
- ngrok = gives localhost a public HTTPS URL
- Docker volume = persistent storage → workflows survive restarts

---

## Files
- workflows/lead-capture-google-sheets.json — exported n8n workflow

---

## Demo Pitch
"Send me a form submission from your website — any form.
I will automatically log it to a spreadsheet in real time.
Here is a live URL → try it right now."

---

