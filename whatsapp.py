"""Thin wrapper around Meta's WhatsApp Cloud API.

Important Meta quirk: outside the 24-hour customer service window, you can only
send pre-approved *template* messages. The window opens whenever the user sends
a message TO your bot. For dev/testing, send a message from her phone to the
bot first, then the bot can reply freely for 24h.
"""
import httpx
from app.config import settings


def _api_url() -> str:
    return f"https://graph.facebook.com/v21.0/{settings.WHATSAPP_PHONE_ID}/messages"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }


async def send_text(to: str, text: str) -> dict:
    """Send a free-form text message. Requires an open 24h window."""
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text, "preview_url": False},
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(_api_url(), headers=_headers(), json=payload)
        if r.status_code >= 400:
            # Surface Meta's error body — it's where the useful info lives
            raise RuntimeError(f"WhatsApp send failed [{r.status_code}]: {r.text}")
        return r.json()


async def send_template(to: str, template_name: str, language_code: str = "en_US") -> dict:
    """Send an approved template. Use this to *open* a conversation if the 24h
    window is closed. Meta provides a default `hello_world` template you can use
    for the first test."""
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
        },
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(_api_url(), headers=_headers(), json=payload)
        if r.status_code >= 400:
            raise RuntimeError(f"WhatsApp template send failed [{r.status_code}]: {r.text}")
        return r.json()
