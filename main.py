from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

@app.get("/")
def read_root():
    return JSONResponse(
        content={"message": "Ваш Backend работает! Привет из TokiBot API."},
        media_type="application/json; charset=utf-8"
    )

@app.get("/send-telegram")
def send_telegram_message():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {"error": "TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не установлены"}

    message = "✅ Ваш бот успешно работает!"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)

    if response.status_code != 200:
        return {"status": response.status_code, "error": response.json()}

    return {"status": response.status_code, "response": response.json()}
