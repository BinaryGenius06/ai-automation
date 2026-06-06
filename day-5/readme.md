# Day 5 — Make.com Survey

## What Was Built
- Make.com account setup
- Webhook → Filter → Google Sheets pipeline (recreation of Day 3 in Make)
- Groq LLM called via HTTP module inside Make
- Written decision framework: n8n vs Make

## Tool Comparison

| | n8n | Make |
|---|---|---|
| Hosting | Self (Docker) | Cloud |
| Free tier | Unlimited | 1000 ops/month |
| UI | Boxes, technical | Bubbles, friendly |
| Client recognition | Low | High ("like Zapier") |
| Best for | Build + deliver | Demo + pitch |

## What the Scenario Does
1. Webhook receives lead (name, email, interest)
2. Filter blocks any email containing "test"
3. Google Sheets → appends row to Hot Leads tab
4. HTTP module → calls Groq → classifies lead as hot/cold

## Make Syntax vs n8n
- n8n: `$json.name` → Make: `{{1.name}}`
- n8n: IF node → Make: Filter (simple) or Route (branching)
- n8n: polling trigger → Make: Watch trigger
- n8n: webhook → Make: Instant trigger

## Key Learnings
- Make has no Groq module → use HTTP → Make an API Key Request
- Make exports Blueprint JSON → check for API keys before pushing
- Make free = 1000 ops/month → demo only, not production
- Credentials in Make are separate from n8n → re-authorize Google fresh

## Files
- `workflows/make-webhook-to-sheets.json` → exported Make scenario blueprint

## Decision Framework