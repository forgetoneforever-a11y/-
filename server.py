import os
import asyncio
import threading
from flask import Flask, request, jsonify
from aiogram import Bot
from aiogram.enums import ParseMode

from bot import dp, bot, TOKEN, MY_TELEGRAM_ID if 'MY_TELEGRAM_ID' in globals() else "ТВОЙ_CHAT_ID"

app = Flask(__name__)

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
    user_id = data.get('user_id', "ТВОЙ_CHAT_ID")

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
    # Запуск бота в фоновом потоке
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()

    # Обязательно берем порт из окружения Render, по умолчанию 10000 (Render любит этот порт)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
