"""Small Telegram reminder service. The existing WhatsApp chat stays separate."""

from contextlib import asynccontextmanager
from datetime import time
import hmac
import logging
import os
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import requests

load_dotenv()
logger = logging.getLogger(__name__)


def reminder_time(name: str, default: str) -> time:
    value = os.getenv(name, default)
    try:
        hour, minute = value.split(":")
        if len(hour) != 2 or len(minute) != 2 or not hour.isdigit() or not minute.isdigit():
            raise ValueError
        return time(int(hour), int(minute))
    except ValueError as exc:
        raise RuntimeError(f"{name} must be in HH:MM (24-hour) format") from exc


def send_telegram(message: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("Telegram environment variables are missing")

    # Never log the request URL or the requests exception: the URL contains the token.
    response = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": message},
        timeout=10,
    )
    if response.status_code != 200 or not response.json().get("ok"):
        raise RuntimeError(f"Telegram send failed (HTTP {response.status_code})")


def deliver_reminder(message: str) -> None:
    try:
        send_telegram(message)
    except Exception:
        logger.error("Reminder delivery failed; check Telegram configuration and connectivity")


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = None
    if os.getenv("REMINDERS_ENABLED", "false").lower() == "true":
        if not os.getenv("TELEGRAM_BOT_TOKEN") or not os.getenv("TELEGRAM_CHAT_ID"):
            raise RuntimeError("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to enable reminders")
        timezone = ZoneInfo(os.getenv("REMINDER_TIMEZONE", "Europe/Istanbul"))
        scheduler = BackgroundScheduler(timezone=timezone)
        reminders = (
            ("stock", "STOCK_REMINDER_TIME", "18:30", "STOCK_REMINDER_TEXT",
             "Bruncha: сверьте продукты и остатки, закажите недостающее."),
            ("cash", "CASH_REMINDER_TIME", "19:00", "CASH_REMINDER_TEXT",
             "Bruncha: отправьте отчёт по кассе за день."),
        )
        for job_id, time_var, default_time, text_var, default_text in reminders:
            when = reminder_time(time_var, default_time)
            scheduler.add_job(
                deliver_reminder, "cron", id=job_id,
                hour=when.hour, minute=when.minute,
                args=[os.getenv(text_var, default_text)],
                coalesce=True, max_instances=1, misfire_grace_time=300,
            )
        scheduler.start()
        logger.info("Daily Telegram reminders started in %s", timezone)
    try:
        yield
    finally:
        if scheduler:
            scheduler.shutdown(wait=False)


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return JSONResponse(
        content={"message": "Ваш Backend работает! Привет из TokiBot API."},
        media_type="application/json; charset=utf-8",
    )


@app.post("/send-telegram")
def send_telegram_message(x_api_key: str | None = Header(default=None)):
    expected = os.getenv("REMINDER_API_KEY")
    if not expected:
        raise HTTPException(status_code=503, detail="Manual sending is disabled")
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        send_telegram("✅ Ваш бот успешно работает!")
    except Exception:
        logger.error("Manual Telegram send failed; check configuration and connectivity")
        raise HTTPException(status_code=502, detail="Telegram delivery failed") from None
    return {"status": "sent"}
