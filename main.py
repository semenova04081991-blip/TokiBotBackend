from fastapi import FastAPI
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = FastAPI()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

@app.get("/send-telegram")
def send_telegram_message():
    message = "✅ Ваш бот успешно работает!"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, data=payload)
    return {"status": response.status_code, "response": response.json()}
