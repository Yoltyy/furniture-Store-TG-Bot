import asyncio
import logging
from aiogram import Dispatcher
from settings.config import bot
from database.engine import async_engine, Base

from handlers.admin import router as admin_router
from handlers.user import router as user_router


async def main():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.include_router(user_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")