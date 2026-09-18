import os
import asyncio
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS  # <--- Обязательно для связи Vercel и Render
from aiogram import Bot
from aiogram.enums import ParseMode

# Безопасный импорт из bot.py
import bot as bot_module

app = Flask(__name__)
CORS(app)  # <--- Разрешаем кросс-доменные запросы с твоего сайта

# Берем токен и ID из импортированного файла bot.py
BOT_TOKEN = getattr(bot_module, "TOKEN", "8902518699:AAFD1yArCMiwoaOn8zPUcubr0W2NemriQlk")
MY_TELEGRAM_ID = getattr(bot_module, "MY_TELEGRAM_ID", "8617178928")
bot = bot_module.bot
dp = bot_module.dp

def run_telegram_bot():
    async def start_polling():
        print("Бот запущен и ожидает сообщения...")
        await dp.start_polling(bot)
    
    asyncio.run(start_polling())

@app.route('/send-note', methods=['POST'])
def receive_note():
    data = request.json
    task_text = data.get('text')
    task_date = data.get('date')
    user_id = data.get('user_id', MY_TELEGRAM_ID)

    if not task_text or not task_date:
        return jsonify({"status": "error", "message": "Missing text or date"}), 400

    message = f"📌 **Новая задача с сайта на {task_date}:**\n{task_text}"

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.MARKDOWN)
        )
        loop.close()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return "Server and Bot are running!", 200

if __name__ == '__main__':
    # Запускаем Telegram-бота в фоновом потоке
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()

    # Запускаем Flask-сервер
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
