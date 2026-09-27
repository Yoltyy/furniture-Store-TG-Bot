import os
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError(
        "Не найден токен бота. Создайте файл .env в корне проекта "
        "(см. .env.example) и укажите в нём BOT_TOKEN=ваш_токен_от_BotFather."
    )

_admin_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: set[int] = {
    int(admin_id.strip())
    for admin_id in _admin_ids_raw.split(",")
    if admin_id.strip().isdigit()
}

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)