# Day 3 — n8n Webhook → Google Sheets Automation

## Overview

Day 3 was about learning the most fundamental automation pattern that exists: something happens → data gets processed → data gets stored somewhere. This pattern is the skeleton of literally every client automation you will ever build.

We set up n8n locally using Docker, built a webhook that accepts any POST request, cleans the data, and appends it as a row in Google Sheets — all in real time. Then we exposed the whole thing to the public internet using ngrok so it can be demoed to anyone, from anywhere, without deploying anything.

---

## Business Problem Being Solved

Every business with a website has a contact form. Most of them:
- Get notified by email
- Manually copy the data into a spreadsheet
- Call everyone one by one

This pipeline automates the first two steps entirely. The moment someone submits a form, the data is already in the spreadsheet. No email to read, no copy-pasting, no delay.

Use cases that pay for this immediately:
- JEE coaching institutes collecting student inquiries
- Freelancers collecting client project requests
- Event companies collecting registrations
- Recruiters collecting job applicants

---

## Tech Stack

- n8n (self-hosted via Docker) → workflow automation engine
- Docker Desktop → runs n8n locally in a container
- Docker Volume → persistent storage so workflows survive restarts
- ngrok free tier → gives localhost a public HTTPS URL
- Google Sheets API → stores lead data
- Google Cloud Console → manages OAuth2 credentials

---

## Architecture

    Webhook (POST /lead-capture)
        ↓
    Edit Fields (flatten body fields + add timestamp)
        ↓
    Google Sheets (Append Row → AI Automation Leads sheet)

Simple. Three nodes. This exact pattern scales to any complexity.

---

## Node by Node Breakdown

### Webhook Node
Listens for incoming HTTP POST requests at a specific path. n8n gives you two URLs:
- Test URL → webhook-test/lead-capture → use while building
- Live URL → webhook/lead-capture → use after activating workflow

Configuration:

    HTTP Method  → POST
    Path         → lead-capture
    Respond      → Immediately (returns 200 without waiting for workflow to finish)

### Edit Fields Node
Takes the raw webhook body and reshapes it into clean, flat fields. Without this node, your data comes nested under body.name, body.email etc. After this node it's just name, email, interest.

Also adds a server-side timestamp so you always know exactly when the lead came in.

| Field | Expression | What it does |
|---|---|---|
| name | {{ $json.body.name }} | Extracts name from webhook body |
| email | {{ $json.body.email }} | Extracts email from webhook body |
| interest | {{ $json.body.interest }} | Extracts interest from webhook body |
| timestamp | {{ new Date().toISOString() }} | Adds current time in ISO format |

### Google Sheets Node
Takes the clean data from Edit Fields and appends it as a new row. Uses OAuth2 to authenticate with Google — no passwords stored anywhere.

Configuration:

    Operation  → Append Row
    Document   → AI Automation Leads
    Sheet      → Sheet1 (renamed to Hot Leads in Day 4)
    Mapping    → Map Each Column Manually

Column mapping:

    A (name)      → {{ $json.name }}
    B (email)     → {{ $json.email }}
    C (interest)  → {{ $json.interest }}
    D (timestamp) → {{ $json.timestamp }}

---

## Docker Setup

### First time only — create volume and run container

    docker volume create n8n_data

    docker run -d `
      --name n8n `
      -p 5678:5678 `
      -v n8n_data:/home/node/.n8n `
      -e GENERIC_TIMEZONE=Asia/Kolkata `
      -e N8N_RUNNERS_ENABLED=true `
      n8nio/n8n

The volume n8n_data persists all your workflows and credentials. Even if you restart the container or your PC, everything is saved.

### Every time after that

    docker start n8n

Then open browser → http://localhost:5678

---

## ngrok Setup

### First time only

    ngrok config add-authtoken YOUR_TOKEN_HERE

Get your token from ngrok.com after signing up (free).

### Every time

    ngrok http 5678

Copy the Forwarding URL that appears:

    Forwarding  https://abc123.ngrok-free.app -> http://localhost:5678

Important: ngrok URL changes every time you restart it on the free tier. This is fine for demos — just share the current URL.

---

## Google Cloud Setup (one-time)

1. Go to console.cloud.google.com → create project named n8n-automation
2. Enable Google Sheets API and Google Drive API
3. OAuth consent screen → External → add your Gmail as test user
4. Credentials → Create OAuth Client ID → Web application
5. Authorized redirect URI → http://localhost:5678/rest/oauth2-credential/callback
6. Copy Client ID + Client Secret → paste into n8n credential → Sign in with Google

This setup is 100% free. Google only charges for massive enterprise scale which you will never hit on personal projects.

---

## Testing

### Local test (PowerShell)

    Invoke-WebRequest -Uri "http://localhost:5678/webhook/lead-capture" -Method POST -ContentType "application/json" -Body '{"name": "Test User", "email": "test@example.com", "interest": "automation"}'

### Public URL test via ngrok

    Invoke-WebRequest -Uri "https://YOUR_NGROK_URL/webhook/lead-capture" -Method POST -ContentType "application/json" -Body '{"name": "Mobile Test", "email": "m@test.com", "interest": "test"}'

Replace YOUR_NGROK_URL with the actual URL from your ngrok terminal.

Expected result: StatusCode 200 + new row appears in Google Sheet within 2-3 seconds.

---

## How to Start Next Time

Step 1 → Open Docker Desktop → wait for whale icon to stop animating

Step 2 → Start n8n container:

    docker start n8n

Step 3 → Open browser → http://localhost:5678 → login

Step 4 → Start ngrok in a separate terminal:

    ngrok http 5678

Step 5 → Copy new ngrok URL → use for testing or sharing

Step 6 → Workflow is already active (Published) → just send a POST request and it runs

---

## Bugs Hit and How They Were Fixed

**venv not having packages installed**
Tried to activate Python venv before running n8n — unrelated issue from earlier days.
Fix: Deactivate venv, run everything globally for this project.

**Google Sheets OAuth failing with access_denied**
n8n app not verified by Google blocked the OAuth flow.
Fix: Add your Gmail as a test user in Google Cloud Console under Audience → Test users.

**timestamp column not appearing in Google Sheets mapping**
n8n only shows columns that exist in row 1 of your sheet.
Fix: Add timestamp as header in D1 of the sheet, then click Refresh Column List in n8n.

**ngrok "Cannot POST /" error**
Sent request to ngrok root URL instead of the webhook path.
Fix: Always append /webhook/lead-capture to the ngrok URL.

---

## Key Concepts Learned

- Webhook = a URL that listens for HTTP POST requests → triggers the workflow when hit
- Edit Fields node = reshapes and renames data as it flows between nodes
- Expressions in n8n use {{ }} syntax → {{ $json.fieldName }} to reference previous node output
- OAuth2 = secure authorization without sharing passwords → Google generates tokens instead
- ngrok = creates a tunnel from the public internet to your localhost → instant public URL
- Docker volume = persistent storage attached to container → data survives restarts
- Workflow must be Published (not just saved) for live webhook URL to work
- Test URL (webhook-test/) only works when clicking "Listen for test event" → Live URL (webhook/) works anytime after activation

---

## Files
- workflows/lead-capture-webhook.json → exported n8n workflow

---

## Demo Pitch

"Send me a form submission from your website — any form, any platform.
I will automatically log it to a spreadsheet in real time.
Here is a live public URL. Try it right now from your phone."

That one sentence closes the demo for any small business owner.

---

## What This Is Worth

Webhook → Sheets is the minimum viable automation. By itself it's worth ₹3,000 - ₹5,000 as a quick freelance job. Combined with the lead qualifier from Day 4, it becomes a ₹10,000 - ₹15,000 product.

---
