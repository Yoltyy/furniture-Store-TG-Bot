from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.states import AddCategoryState
from keyboard.button_template import admin_kb, build_cancel_kb
from keyboard.keyboard_builder import make_button
from database.requests import add_category

router = Router()


@router.callback_query(F.data == "new_category_furniture")
async def start_add_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddCategoryState.name)
    kb = make_button(build_cancel_kb)
    await callback.message.edit_text("Введите название новой категории:", reply_markup=kb)
    await callback.answer()


@router.message(AddCategoryState.name)
async def process_cat_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("⚠️ Название не может быть пустым. Введите название категории:")
        return

    await state.update_data(name=name)
    await state.set_state(AddCategoryState.description)
    kb = make_button(build_cancel_kb)
    await message.answer("Введите описание категории (или напишите 'пропустить'):", reply_markup=kb)


@router.message(AddCategoryState.description)
async def process_cat_desc(message: Message, state: FSMContext):
    data = await state.get_data()
    desc = None if message.text.strip().lower() == "пропустить" else message.text.strip()

    success = await add_category(name=data['name'], description=desc)
    kb = make_button(admin_kb, sizes=(2, 2, 1, 1))

    if success:
        await message.answer(f"✅ Категория '{data['name']}' успешно создана!", reply_markup=kb)
    else:
        await message.answer("⚠️ Ошибка: Категория с таким именем уже существует.", reply_markup=kb)

    await state.clear()