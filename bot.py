# bot.py

import asyncio
import logging
import argparse

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from application.container import Container
from presentation.routers import all_routers

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not configured. Set it in .env or environment variables.")

# Логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Бот з правильним parse_mode для Aiogram 3.7+
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Підключаємо всі роутери
for router in all_routers:
    dp.include_router(router)

# CLI-режим: ручне оголошення
async def run_announce_mode():
    container = Container(bot=bot)
    push_service = container.push

    if not push_service.push_targets:
        print("❌ Немає чатів у PUSH_TARGETS")
        return

    print("\nДоступні чати:")
    for i, target in enumerate(push_service.push_targets, 1):
        thread = f" (thread {target.get('thread_id')})" if target.get("thread_id") else ""
        print(f"  {i}. chat_id={target['chat_id']}{thread}")
    print(f"  {len(push_service.push_targets) + 1}. Всім одразу")

    while True:
        try:
            choice = int(input("\nНомер чату (або для всіх): ").strip())
            if 1 <= choice <= len(push_service.push_targets) + 1:
                break
        except ValueError:
            pass
        print("Введіть правильний номер")

    targets = push_service.push_targets if choice == len(push_service.push_targets) + 1 else [push_service.push_targets[choice - 1]]

    text = input("\nТекст оголошення (HTML дозволено): ").strip()
    if not text:
        print("Текст порожній — скасовано")
        return

    await push_service.send_announcement(text, targets=targets)
    print("Готово!")


# Звичайний запуск бота
async def main():
    print("🚀 Бот запущено — нова архітектура з контейнером!")
    Container.init(bot=bot)

    container = Container.get()

    # Scheduler: нагадування + дайджест
    scheduler = container.update_scheduler
    scheduler.start()
    print("📅 Scheduler запущено")

    # Polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--announce", action="store_true", help="Ручне оголошення з консолі")

    args = parser.parse_args()

    if args.announce:
        asyncio.run(run_announce_mode())
    else:
        asyncio.run(main())
