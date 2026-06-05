# Day 4 — AI Lead Qualifier (Gmail Trigger + Groq Scoring)

## Overview

So the idea here was simple but powerful: instead of manually reading every email and deciding if someone is worth calling, why not let an AI do it automatically?

By the end of Day 4, any email sent to binarygenius.leads@gmail.com gets read by n8n, classified by Groq as hot/warm/cold, logged to the right Google Sheet, and if it's a hot lead — Suryansh gets an alert AND the sender gets a personalized reply. Zero human involvement required.

This is the kind of automation that businesses actually pay for. A JEE coaching institute getting 100 inquiry emails a week doesn't want to read all of them. They want to know which 10 are serious. That's exactly what this does.

---

## Business Problem Being Solved

Manual lead qualification is expensive and slow:
- Sales team reads 100 emails → calls 100 people → 80 are time wasters
- With this pipeline → AI reads 100 emails → flags 15 hot leads → sales team only calls those 15
- Time saved per week: 5-10 hours
- Commercial value: ₹10,000 - ₹15,000 as a one-time automation setup

---

## Tech Stack

- n8n (self-hosted via Docker) → workflow automation engine
- Gmail API → reading incoming emails + sending replies
- Groq API (Llama 3.3-70b) → AI classification + reply generation
- Google Sheets API → storing classified leads
- Google Cloud Console → OAuth2 credentials management

---

## Architecture

    Gmail Trigger (polls binarygenius.leads@gmail.com every 1 min)
        ↓
    Edit Fields (extract + clean name, email, body from raw email data)
        ↓
    HTTP Request → Groq API (classify lead as hot/warm/cold)
        ↓
    Code Node in JavaScript (parse Groq JSON response safely)
        ↓
    IF Node (score contains "hot"?)
        ↓ TRUE                                    ↓ FALSE
    Append to Hot Leads Sheet              IF Node (score contains "warm"?)
        ↓                                      ↓ TRUE           ↓ FALSE
    HTTP Request → Groq API            Warm Leads Sheet    Cold Leads Sheet
    (generate personalized reply)
        ↓
    Code Node (extract reply text)
        ↓
    Gmail → Send alert to suryansh2020uttam.knp@gmail.com
        ↓
    Gmail → Send auto-reply to lead's email

---

## Lead Scoring Logic

The system prompt given to Groq defines exactly what hot, warm, and cold mean:

    Hot lead = specific use case mentioned, business email domain, clear intent,
               mentions team size or budget or timeline

    Warm lead = genuine interest, real full name, some context given,
                personal gmail okay IF they explain their business clearly

    Cold lead = one-line message with no context, no name given, vague words
                like "hi" or "lmk" or "just checking", random numbers in email,
                message under 20 words with no specifics

    When in doubt between warm and cold → choose cold

Key design decision: default to cold when uncertain. Better to miss a warm lead than waste time on cold ones.

---

## Node by Node Breakdown

### Gmail Trigger
Polls the inbox every 1 minute for new unread emails. Returns raw email data including headers, body, sender info.

Important: Simplify must be turned OFF to get structured sender data with name and address fields.

### Edit Fields
Extracts clean data from raw Gmail output:

    name     → {{ $json.from.value[0].name }}
    email    → {{ $json.from.value[0].address }}
    interest → {{ $json.text.replace(/\n/g, ' ').replace(/\r/g, '').trim() }}

Critical learning: email body contains newline characters that break JSON. Must clean at source before passing to any HTTP Request node.

### HTTP Request (Groq Classify)
Calls Groq REST API directly since n8n has no native Groq node. Pattern works for any REST API.

    Method: POST
    URL: https://api.groq.com/openai/v1/chat/completions
    Auth: Bearer token via Header Auth credential
    Temperature: 0 (deterministic — same input = same output)

Full JSON body:

    {
      "model": "llama-3.3-70b-versatile",
      "temperature": 0,
      "messages": [
        {
          "role": "system",
          "content": "You are a lead qualification assistant. Analyze the lead and respond with ONLY a JSON object in this exact format: {\"score\": \"hot\" or \"warm\" or \"cold\", \"reason\": \"one sentence\"}\n\nHot lead = specific use case mentioned, business email domain, clear intent, mentions team size or budget or timeline.\nWarm lead = genuine interest, real full name, some context given, personal gmail okay IF they explain their business clearly.\nCold lead = ANY of these: one-line message with no context, no name given, vague words like hi or lmk or just checking, random numbers in email, message under 20 words with no specifics.\n\nWhen in doubt between warm and cold, choose cold.\nShort vague emails with no business context are always cold."
        },
        {
          "role": "user",
          "content": "={{ 'Name: ' + $json.name + '\\nEmail: ' + $json.email + '\\nInterest: ' + $json.interest.replace(/\n/g, ' ') }}"
        }
      ]
    }

### Code Node (Parse Groq Response)
Extracts score and reason from nested Groq response, handles edge cases:

    const rawContent = $input.first().json.choices[0].message.content.trim();

    let cleaned = rawContent;
    if (cleaned.includes("```")) {
      cleaned = cleaned.split("```")[1] || cleaned;
      if (cleaned.startsWith("json")) cleaned = cleaned.slice(4);
      cleaned = cleaned.trim();
    }

    let parsed;
    try {
      parsed = JSON.parse(cleaned);
    } catch(e) {
      parsed = { score: "cold", reason: "parse error: " + e.message };
    }

    return [{
      json: {
        name: $('Edit Fields').first().json.name,
        email: $('Edit Fields').first().json.email,
        interest: $('Edit Fields').first().json.interest,
        timestamp: $('Edit Fields').first().json.timestamp,
        score: parsed.score.toLowerCase().trim(),
        reason: parsed.reason
      }
    }];

### IF Nodes (Branching)
Two IF nodes create three paths:
- First IF: score contains "hot" → TRUE goes to hot pipeline, FALSE goes to second IF
- Second IF: score contains "warm" → TRUE goes to Warm Leads, FALSE goes to Cold Leads

Important: Use "contains" not "is equal to" — avoids type mismatch issues in n8n.

### Google Sheets Nodes
Three separate Append Row nodes, one per sheet tab:
- Hot Leads → name, email, interest, timestamp, score, reason
- Warm Leads → same fields
- Cold Leads → same fields

### HTTP Request (Groq Auto-Reply)
Only fires for hot leads. Calls Groq again with temperature 0.7 to generate personalized reply:

    {
      "model": "llama-3.3-70b-versatile",
      "temperature": 0.7,
      "messages": [
        {
          "role": "system",
          "content": "You are a professional automation consultant. Write a short, warm, personalized email reply to a potential client who just submitted an inquiry. Be concise (3-4 sentences max). Sound human, not robotic. Sign off as Suryansh, AI Automation Consultant."
        },
        {
          "role": "user",
          "content": "={{ 'Write a reply to this lead:\\nName: ' + $json.name + '\\nInterest: ' + $json.interest.replace(/\\n/g, ' ') + '\\nReason they are hot: ' + $json.reason }}"
        }
      ]
    }

### Gmail Alert + Auto-Reply
Two Gmail nodes at end of hot lead pipeline:
- Send a message → alert to suryansh2020uttam.knp@gmail.com with lead details
- Send a message1 → personalized Groq-written reply to the lead

Both send FROM binarygenius.leads@gmail.com using Gmail account 2 credential.

To field for reply node must reference Code in JavaScript1 directly:

    To      → {{ $('Code in JavaScript1').first().json.email }}
    Message → {{ $('Code in JavaScript1').first().json.reply }}

---

## Google Cloud Setup (one-time)

1. console.cloud.google.com → project: n8n-automation
2. Enable: Google Sheets API, Google Drive API, Gmail API
3. OAuth consent screen → External → add both Gmail accounts as test users
4. Credentials → OAuth Client ID → Web application
5. Redirect URI → http://localhost:5678/rest/oauth2-credential/callback
6. Create two credentials in n8n:
   - Gmail account → suryansh2020uttam.knp@gmail.com
   - Gmail account 2 → binarygenius.leads@gmail.com

---

## Google Sheets Structure

Three tabs in AI Automation Leads spreadsheet:

    Hot Leads:  name | email | interest | timestamp | score | reason
    Warm Leads: name | email | interest | timestamp | score | reason
    Cold Leads: name | email | interest | timestamp | score | reason

---

## Bugs Hit and How They Were Fixed

**Newlines breaking JSON**
Email body text contains newline characters. When passed directly into HTTP Request JSON body, throws "Bad control character" error.
Fix: Clean in Edit Fields node using .replace(/\n/g, ' ').replace(/\r/g, '').trim()

**IF node "is equal to" not working**
Score value "warm" was not matching condition "warm" due to internal type mismatch in n8n.
Fix: Changed operator from "is equal to" to "contains" — bypasses type comparison entirely.

**Auto-reply Gmail node receiving undefined fields**
Gmail alert node output returns Gmail API response, not lead data fields.
Fix: Reference Code in JavaScript1 node directly using $('Code in JavaScript1').first().json.email

**Gmail Trigger not auto-firing**
Workflow published but not picking up new emails automatically.
Fix: Turn Simplify OFF in Gmail Trigger node. Ensure emails stay UNREAD before n8n polls.

**Warm leads routing to Cold Leads sheet**
IF1 node sending warm scored leads to FALSE branch.
Fix: Switching from "is equal to" to "contains" fixed routing.

**Alert emails going to spam**
Lead alert emails sent from binarygenius.leads to suryansh2020uttam were landing in spam.
Fix: Mark as Not Spam once → Gmail learns and future alerts go to inbox.

---

## Test Cases and Results

| Email Type | Score | Correct |
|---|---|---|
| Recruitment agency, 15 people, ₹20k budget, business email | Hot | Yes |
| "hi can you help me lmk" | Cold | Yes (after prompt fix) |
| Small tutoring business, exploring options | Warm | Yes |
| WhatsApp bot for clothing store, ₹30k budget | Hot | Yes |
| HR firm, 30 resumes/week, no budget mentioned | Warm | Yes |

---

## Files
- workflows/lead-qualifier-gmail-trigger.json → exported n8n workflow

---

## Key Concepts Learned

- Gmail Trigger polls every 1 min → good enough for business use
- HTTP Request node calls any REST API → universal integration pattern
- Code nodes use full JavaScript → not limited to n8n expressions
- Two Gmail accounts → dedicated business inbox + personal alert inbox
- Prompt engineering controls AI behavior → small wording changes = big output differences
- "When in doubt choose cold" → better business logic than being generous with warm
- IF node "contains" more reliable than "is equal to" for string comparisons in n8n

---

## What This Is Worth

A coaching institute running Google Ads gets 50-100 inquiry emails per week.
They manually read all of them and call everyone. You automate the triage.
They only call hot leads. 5-10 hours per week saved.
One-time setup fee: ₹10,000 - ₹15,000.

---

