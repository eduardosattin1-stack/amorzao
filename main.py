"""amor-bot — Step 1 thin slice.

Goal of this slice: prove the WhatsApp loop works end-to-end.
- GET  /webhook  → Meta verification handshake (one-time).
- POST /webhook  → receive incoming messages, log them, echo back.
- GET  /health   → uptime check.

No DB, no LLM, no SRS yet. We add those once this loop is solid.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.whatsapp import send_text

app = FastAPI(title="amor-bot")

LOG_PATH = Path("data/interactions.jsonl")


def log_event(kind: str, payload: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            "payload": payload,
        }, ensure_ascii=False) + "\n")


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


@app.get("/webhook", response_class=PlainTextResponse)
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
) -> str:
    """Meta hits this once with a verify_token of our choosing.
    We echo back hub.challenge if the token matches."""
    if hub_mode == "subscribe" and hub_verify_token == settings.WEBHOOK_VERIFY_TOKEN:
        return hub_challenge
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook")
async def receive_webhook(request: Request) -> dict:
    body = await request.json()
    log_event("inbound_raw", body)

    # Meta wraps payloads several layers deep. Status updates (sent/delivered/read)
    # come through this same endpoint with no `messages` array — ignore those.
    try:
        value = body["entry"][0]["changes"][0]["value"]
    except (KeyError, IndexError):
        return {"ok": True}

    for msg in value.get("messages", []):
        from_number = msg.get("from")
        msg_type = msg.get("type")
        text = (
            msg.get("text", {}).get("body", "")
            if msg_type == "text"
            else f"[non-text: {msg_type}]"
        )

        log_event("inbound_message", {"from": from_number, "type": msg_type, "text": text})
        print(f"📨 from {from_number}: {text}")

        # Thin-slice behavior: echo back. Replace this with real challenge logic later.
        reply = f"Recebi: {text!r} ✅ (bot funcionando)"
        try:
            await send_text(from_number, reply)
            log_event("outbound_message", {"to": from_number, "text": reply})
        except Exception as e:
            log_event("outbound_error", {"to": from_number, "error": str(e)})
            print(f"⚠️  send failed: {e}")

    return {"ok": True}
