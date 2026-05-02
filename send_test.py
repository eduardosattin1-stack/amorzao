"""Manually send a message to the configured recipient. Run this first to
verify your token + phone-id work, before bothering with webhooks.

    python scripts/send_test.py
    python scripts/send_test.py "custom message here"
    python scripts/send_test.py --template hello_world

If the 24h window is closed, free-form sends will fail with a 'recipient phone
number not in allowed list' or '24-hour window expired' error. Send a template
first, OR have her message the bot from her phone, then retry.
"""
import asyncio
import sys
from pathlib import Path

# Make `app` importable when run from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.whatsapp import send_template, send_text


async def main() -> None:
    args = sys.argv[1:]

    if args and args[0] == "--template":
        name = args[1] if len(args) > 1 else "hello_world"
        print(f"→ Sending template '{name}' to {settings.GIRLFRIEND_PHONE}")
        result = await send_template(settings.GIRLFRIEND_PHONE, name)
    else:
        text = " ".join(args) if args else "Oi! Teste do bot 🇧🇷"
        print(f"→ Sending text to {settings.GIRLFRIEND_PHONE}: {text}")
        result = await send_text(settings.GIRLFRIEND_PHONE, text)

    print("✅", result)


if __name__ == "__main__":
    asyncio.run(main())
