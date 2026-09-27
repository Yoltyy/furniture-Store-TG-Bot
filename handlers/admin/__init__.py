from aiogram import Router

from .main_admin import router as main_admin_router
from .new_category_furniture_handler import router as new_category_router
from .new_furniture_handler import router as new_furniture_router
from .list_category_furniture_handler import router as list_category_router
from filters.admin_filter import IsAdmin

router = Router()

# Фильтр на уровне корневого роутера админки: проверяется раньше любых
# хендлеров внутри него и внутри всех вложенных роутеров ниже, так что
# закрывает доступ сразу ко всей админ-панели, а не к отдельным кнопкам.
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

router.include_router(main_admin_router)
router.include_router(new_category_router)
router.include_router(new_furniture_router)
router.include_router(list_category_router)