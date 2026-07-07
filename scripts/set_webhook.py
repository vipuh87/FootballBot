import asyncio

import httpx

from config import BOT_TOKEN, PUBLIC_BASE_URL, WEBHOOK_SECRET


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not configured")
    if not PUBLIC_BASE_URL:
        raise RuntimeError("PUBLIC_BASE_URL is not configured")
    if not WEBHOOK_SECRET:
        raise RuntimeError("WEBHOOK_SECRET is not configured")

    url = f"{PUBLIC_BASE_URL}/api/webhook"
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            api_url,
            json={
                "url": url,
                "secret_token": WEBHOOK_SECRET,
                "drop_pending_updates": True,
                "allowed_updates": ["message", "callback_query"],
            },
        )
        response.raise_for_status()
        print(response.json())


if __name__ == "__main__":
    asyncio.run(main())
