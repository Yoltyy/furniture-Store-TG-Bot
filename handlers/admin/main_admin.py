from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboard.button_template import admin_kb, furniture_cancel_kb
from keyboard.keyboard_builder import make_button
from states.states import RemoveFurnitureState
from database.requests import delete_furniture_by_id, get_cooperation_requests

router = Router()


@router.message(Command("admin_panel"))
async def admin_panel_cmd(message: Message):
    kb = make_button(admin_kb, sizes=(2, 2, 1, 1))
    await message.answer("🔧 <b>Панель администратора</b>\nВыберите действие:", reply_markup=kb)


@router.callback_query(F.data.in_({"cancel_category", "cancel_furniture"}))
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    kb = make_button(admin_kb, sizes=(2, 2, 1, 1))
    await callback.message.edit_text("❌ Действие отменено.", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "remowed_furniture")
async def start_remove_furniture(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RemoveFurnitureState.furniture_id)
    kb = make_button(furniture_cancel_kb)
    await callback.message.edit_text(
        "Введите ID товара, который нужно удалить.\n"
        "Посмотреть ID можно в разделе «Список товаров»: выберите категорию — там будут ID всех товаров в ней.",
        reply_markup=kb,
    )
    await callback.answer()


@router.message(RemoveFurnitureState.furniture_id)
async def process_remove_furniture(message: Message, state: FSMContext):
    raw_id = message.text.strip()

    if not raw_id.isdigit():
        await message.answer("⚠️ ID должен быть числом. Введите ID товара ещё раз:")
        return

    deleted = await delete_furniture_by_id(int(raw_id))
    kb = make_button(admin_kb, sizes=(2, 2, 1, 1))

    if deleted:
        await message.answer(f"✅ Товар с ID {raw_id} удалён из базы.", reply_markup=kb)
    else:
        await message.answer(f"⚠️ Товар с ID {raw_id} не найден.", reply_markup=kb)

    await state.clear()


@router.callback_query(F.data == "cooperation_categories")
async def show_cooperation_requests(callback: CallbackQuery):
    requests = await get_cooperation_requests()

    if not requests:
        await callback.message.answer("📭 Заявок на сотрудничество пока нет.")
        await callback.answer()
        return

    lines = ["🤝 <b>Заявки на сотрудничество:</b>\n"]
    for idx, req in enumerate(requests, start=1):
        username = f"@{req.username}" if req.username else "без username"
        name = req.first_name or "без имени"
        date_str = req.created_at.strftime("%d.%m.%Y %H:%M") if req.created_at else "—"
        lines.append(f"{idx}. {name} ({username}) — id: {req.telegram_id} — {date_str}")

    await callback.message.answer("\n".join(lines), parse_mode="HTML")
    await callback.answer()