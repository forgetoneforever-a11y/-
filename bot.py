import json
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession

TOKEN = "8902518699:AAFD1yArCMiwoaOn8zPUcubr0W2NemriQlk"

# Сессия с таймаутом для стабильной локальной работы
session = AiohttpSession(timeout=30)
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

DATA_FILE = "data.json"


def load_data():
  if not os.path.exists(DATA_FILE):
    return {"notes": [], "schedule": []}
  with open(DATA_FILE, "r", encoding="utf-8") as f:
    return json.load(f)


def save_data(data):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
  await message.answer(
      "👋 Привет! Я твой учебный бот-помощник.\n\n"
      "📌 **Команды:**\n"
      "• `/tasks` — показать все задачи с сайта\n"
      "• `/add <текст>` — добавить новую задачу прямо из Telegram\n\n"
      "Синхронизация с сайтом работает в реальном времени! 🚀"
  )


@dp.message(Command("tasks"))
async def cmd_tasks(message: types.Message):
  data = load_data()
  notes = data.get("notes", [])

  if not notes:
    await message.answer(
        "📭 Список задач пока пуст. Добавь что-нибудь на сайте или через"
        " `/add Текст`!"
    )
    return

  text = "📝 **Твои текущие задачи:**\n\n"
  for i, note in enumerate(notes, 1):
    text += f"{i}. {note['text']}\n"

  await message.answer(text, parse_mode="Markdown")


@dp.message(Command("add"))
async def cmd_add(message: types.Message):
  args = message.text.split(maxsplit=1)
  if len(args) < 2:
    await message.answer(
        "⚠️ Укажи текст задачи.\nПример: `/add Сделать лабу`",
        parse_mode="Markdown",
    )
    return

  task_text = args[1]
  data = load_data()
  data["notes"].append({"text": task_text})
  save_data(data)

  await message.answer(
      f"✅ **Задача добавлена!**\n`{task_text}`", parse_mode="Markdown"
  )


async def main():
  print("Бот запущен и готов к работе...")
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())