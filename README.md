# amor-bot

A WhatsApp bot that sends daily Brazilian Portuguese vocab challenges. This
repo currently contains **Step 1: the thin slice** — proves the WhatsApp
loop works end-to-end (send → receive → reply). DB, SRS, LLM grading, and
challenge formats come in later steps.

## Prerequisites

- Python 3.11+
- A Meta developer app with WhatsApp product enabled (see top-level chat for
  the manual setup steps)
- [`ngrok`](https://ngrok.com/download) installed for exposing your local
  server to Meta's webhook

## Setup

```bash
# 1. Install deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Then edit .env with your real values
```

## Run the loop

You'll need **three terminals**.

### Terminal 1 — the API

```bash
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 — ngrok tunnel (exposes localhost:8000 to the internet)

```bash
ngrok http 8000
```

Copy the `https://....ngrok-free.app` URL it prints.

### Terminal 3 — manual send test (do this FIRST)

```bash
# This proves outbound works without involving webhooks at all
python scripts/send_test.py --template hello_world
```

If she gets the message, your token + phone ID are correct. ✅

## Register the webhook with Meta

Back in the Meta app dashboard:

1. WhatsApp → Configuration → **Webhook** → "Edit"
2. **Callback URL**: `https://YOUR-NGROK-URL.ngrok-free.app/webhook`
3. **Verify token**: paste the same string you put in `.env` as `WEBHOOK_VERIFY_TOKEN`
4. Click "Verify and save". Meta will GET your `/webhook` and you'll see a
   200 OK in the uvicorn logs.
5. Subscribe to the **`messages`** field under "Webhook fields".

## Test the full loop

From **your girlfriend's phone**, send a WhatsApp message to your test number.

You should see:

- An `inbound_message` line in the uvicorn logs
- A reply on her phone: `Recebi: '<her text>' ✅ (bot funcionando)`
- New rows in `data/interactions.jsonl`

That's the thin slice complete. 🎉

## Common gotchas

- **Free-form sends fail with "24-hour window expired"** — Meta only allows
  free-form messages within 24h of the user messaging *you*. Until then,
  send templates only. Once she texts the bot, the window opens.
- **ngrok URL changes every restart** on the free plan. Re-paste the new
  URL into Meta's webhook config each time. (Or pay for a static domain —
  worth $10/mo once you're past prototyping.)
- **Test number can only message verified recipients.** Add her number under
  WhatsApp → API Setup → "To" → "Manage phone number list".
- **Temporary token expires in 24h.** For overnight testing, generate a
  System User access token in Business Manager (permanent). Do this *after*
  the thin slice works, not before.

## Next steps (Step 2)

Once the loop is solid:
- Postgres + Supabase
- `vocabulary` and `user_progress` tables
- Replace the echo with a real challenge (start with multiple choice,
  hardcoded word list)
- LLM grading via the Anthropic SDK for free-form answers

## Layout

```
amor-bot/
├── app/
│   ├── config.py       # env-var loading
│   ├── main.py         # FastAPI app: webhook + echo
│   └── whatsapp.py     # Meta Graph API client
├── scripts/
│   └── send_test.py    # manual outbound test
├── data/               # interactions.jsonl lives here (gitignored)
├── .env.example
├── requirements.txt
└── README.md
```
