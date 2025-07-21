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
    return JSONResponse(content={"message": "Вы запустили Backend сервиса! Добро пожаловать в TokiBot API."})

@app.get("/send-telegram")
def send_telegram_message():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return JSONResponse(
            content={"error": "TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не установлены"},
            status_code=400
        )

    message = "✅ Ваш бот успешно работает!"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    return JSONResponse(content={"status": response.status_code, "response": response.json()})
