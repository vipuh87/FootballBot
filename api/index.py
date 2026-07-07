from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request

from application.container import Container
from bot import bot, dp
from config import CRON_SECRET, WEBHOOK_SECRET


app = FastAPI()


def container() -> Container:
    return Container.init(bot=bot)


@app.get("/")
async def health():
    return {"ok": True}


@app.get("/api/health")
async def api_health():
    return {"ok": True}


@app.post("/api/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    if WEBHOOK_SECRET and x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret")

    container()
    data = await request.json()
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/api/cron")
async def cron_tick(authorization: str | None = Header(default=None)):
    if CRON_SECRET:
        expected = f"Bearer {CRON_SECRET}"
        if authorization != expected:
            raise HTTPException(status_code=401, detail="Invalid cron secret")

    c = container()
    await c.update_scheduler.run_cron_tick()
    return {"ok": True}
