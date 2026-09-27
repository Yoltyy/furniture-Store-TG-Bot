import re

from aiogram import Router, F, types

from database.requests import get_categories, get_category_by_id, get_furniture_by_category
from keyboard.button_template import admin_kb
from keyboard.keyboard_builder import make_button

router = Router()

CATEGORY_CALLBACK_PREFIX = "admin_view_cat_"


def _short_description(description: str, limit: int = 70) -> str:
    """Убирает HTML-теги и обрезает описание для компактного отображения в списке."""
    plain = re.sub(r"<[^>]+>", "", description or "").strip()
    plain = " ".join(plain.split())
    if len(plain) > limit:
        plain = plain[:limit].rstrip() + "…"
    return plain or "(без описания)"


@router.callback_query(F.data == "list_furniture")
async def list_furniture_categories(callback_query: types.CallbackQuery):
    categories = await get_categories()

    if not categories:
        kb = make_button(admin_kb, sizes=(2, 2, 1, 1))
        await callback_query.message.edit_text(
            "Пока нет ни одной категории мебели.",
            reply_markup=kb,
        )
        await callback_query.answer()
        return

    buttons = [(category.name, f"{CATEGORY_CALLBACK_PREFIX}{category.id}") for category in categories]
    buttons.append(("⬅️ Назад", "back_to_admin_panel"))
    kb = make_button(buttons, sizes=(1,))

    await callback_query.message.edit_text(
        "📁 Выберите категорию, чтобы увидеть список товаров и их ID:",
        reply_markup=kb,
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith(CATEGORY_CALLBACK_PREFIX))
async def list_furniture_in_category(callback_query: types.CallbackQuery):
    category_id = callback_query.data.replace(CATEGORY_CALLBACK_PREFIX, "")
    category = await get_category_by_id(int(category_id))

    if not category:
        await callback_query.answer("⚠️ Категория не найдена.", show_alert=True)
        return

    items = await get_furniture_by_category(category_name=category.name)

    back_kb = make_button([("⬅️ К списку категорий", "list_furniture")], sizes=(1,))

    if not items:
        await callback_query.message.edit_text(
            f"В категории «{category.name}» пока нет товаров.",
            reply_markup=back_kb,
        )
        await callback_query.answer()
        return

    lines = [f"📦 <b>Товары в категории «{category.name}»:</b>\n"]
    for item in items:
        lines.append(f"• ID: <code>{item.id}</code> — {_short_description(item.description)}")

    lines.append("\nЧтобы удалить товар, нажмите «Удалить мебель» в меню админки и введите нужный ID.")

    await callback_query.message.edit_text(
        "\n".join(lines),
        reply_markup=back_kb,
        parse_mode="HTML",
    )
    await callback_query.answer()


@router.callback_query(F.data == "back_to_admin_panel")
async def back_to_admin_panel(callback_query: types.CallbackQuery):
    kb = make_button(admin_kb, sizes=(2, 2, 1, 1))
    await callback_query.message.edit_text(
        "🔧 <b>Панель администратора</b>\nВыберите действие:",
        reply_markup=kb,
    )
    await callback_query.answer()
