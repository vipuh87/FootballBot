import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN

from presentation import all_routers
from application.container import Container
from application.services.update_scheduler import UpdateScheduler


async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Один раз створюємо всі сервіси
    Container.init(bot)

    # Реєструємо роутери
    for router in all_routers:
        dp.include_router(router)

    # Запускаємо планувальник, використовуючи контейнер
    scheduler = UpdateScheduler(
        api=Container.get().api,
        cache=Container.get().cache,
        limiter=Container.get().limiter,
        push=Container.get().push,
        bot=bot
    )
    scheduler.start()

    print("🚀 Бот запущено — нова архітектура з контейнером!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())