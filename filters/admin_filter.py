from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from settings.config import ADMIN_IDS


class IsAdmin(BaseFilter):
    """
    Пропускает событие дальше, только если его отправитель есть в ADMIN_IDS
    (см. settings/config.py, значения берутся из .env -> ADMIN_IDS).
    Работает и для Message, и для CallbackQuery, так как у обоих есть from_user.
    """

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return event.from_user is not None and event.from_user.id in ADMIN_IDS
