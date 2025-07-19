# Toki Bot Backend

## 📦 Требования
- Python 3.9+
- Uvicorn, FastAPI, dotenv, apscheduler

## 🚀 Запуск локально

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## 🚀 Деплой на Render

1. Создай репозиторий на GitHub.
2. Зали файл проекта:

- `main.py`
- `requirements.txt`
- `Procfile`
- `.env.example`
- `README.md`

3. Подключи репозиторий на [https://render.com](https://render.com) как Web Service.
4. Build Command:
```
pip install -r requirements.txt
```
5. Start Command:
```
uvicorn main:app --host=0.0.0.0 --port=8000
```
6. Укажи переменные окружения:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

7. Нажми Deploy.

После деплоя проверь `/send-telegram` в браузере или Postman — должно прийти сообщение в Telegram.
