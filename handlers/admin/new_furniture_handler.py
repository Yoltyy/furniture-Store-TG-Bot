from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.states import AddFurnitureState
from keyboard.button_template import (
    admin_kb,
    furniture_cancel_kb,
    country_of_origin_kb,
    kitchen_type_kb,
    finish_photos_kb,
)
from keyboard.keyboard_builder import make_button
from database.requests import get_categories, add_furniture

router = Router()

DEFAULT_KITCHEN_COUNTRY = "Россия"
KITCHEN_KEYWORD = "кухон"


@router.callback_query(F.data == "new_furniture")
async def start_add_furniture(callback: CallbackQuery, state: FSMContext):
    categories = await get_categories()
    if not categories:
        await callback.answer("Сначала добавьте хотя бы одну категорию!", show_alert=True)
        return

    cat_buttons = [(cat.name, f"select_cat_{cat.id}") for cat in categories]
    cat_buttons.append(("Отменить", "cancel_furniture"))

    await state.update_data(category_lookup={str(cat.id): cat.name for cat in categories})

    kb = make_button(cat_buttons)
    await state.set_state(AddFurnitureState.category)
    await callback.message.edit_text("Шаг 1: Выберите категорию товара из списка:", reply_markup=kb)
    await callback.answer()


@router.callback_query(AddFurnitureState.category, F.data.startswith("select_cat_"))
async def process_furn_cat(callback: CallbackQuery, state: FSMContext):
    cat_id = callback.data.replace("select_cat_", "")
    data = await state.get_data()
    cat_name = data.get("category_lookup", {}).get(cat_id)

    if not cat_name:
        await callback.answer("⚠️ Категория не найдена, попробуйте снова.", show_alert=True)
        return

    is_kitchen = KITCHEN_KEYWORD in cat_name.lower()
    await state.update_data(category=cat_name, is_kitchen=is_kitchen)
    await state.set_state(AddFurnitureState.type_or_country)

    if is_kitchen:
        kb = make_button(kitchen_type_kb)
        text = "Шаг 2: Выберите тип кухни:"
    else:
        kb = make_button(country_of_origin_kb)
        text = "Шаг 2: Выберите страну производителя:"

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(AddFurnitureState.type_or_country)
async def process_furn_type(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    is_kitchen = data.get("is_kitchen", False)

    kitchen_map = {"straight_kitchen": "Прямая кухня", "corner_kitchen": "Угловая кухня"}
    country_map = {"russia_origin": "Россия", "turkey_origin": "Турция"}

    if is_kitchen:
        kitchen_type = kitchen_map.get(callback.data)
        if not kitchen_type:
            await callback.answer("⚠️ Пожалуйста, выберите тип кухни из списка.", show_alert=True)
            return
        await state.update_data(kitchen_type=kitchen_type, country=DEFAULT_KITCHEN_COUNTRY)
    else:
        country = country_map.get(callback.data)
        if not country:
            await callback.answer("⚠️ Пожалуйста, выберите страну из списка.", show_alert=True)
            return
        await state.update_data(kitchen_type=None, country=country)

    await state.set_state(AddFurnitureState.description)
    kb = make_button(furniture_cancel_kb)
    await callback.message.edit_text(
        "Шаг 3: Отправьте полное описание товара (название, размеры, материал, цена):",
        reply_markup=kb,
    )
    await callback.answer()


@router.message(AddFurnitureState.description)
async def process_furn_desc(message: Message, state: FSMContext):
    description = message.text.strip()
    if not description:
        await message.answer("⚠️ Описание не может быть пустым. Пожалуйста, введите описание товара:")
        return

    await state.update_data(description=description, photos=[])
    await state.set_state(AddFurnitureState.photos)

    kb = make_button(finish_photos_kb)
    await message.answer(
        "Шаг 4: Отправьте фотографии товара (от 1 до 10 шт.). Нажмите кнопку «Завершить...», когда загрузите все:",
        reply_markup=kb,
    )


@router.message(AddFurnitureState.photos, F.photo)
async def process_furn_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])

    if len(photos) >= 10:
        await message.answer("⚠️ Достигнут лимит в 10 фото. Нажмите «Завершить загрузку фото».")
        return

    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer(f"📸 Фото добавлено ({len(photos)}/10).")


@router.callback_query(AddFurnitureState.photos, F.data == "finish_photos")
async def finish_furn(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])

    if not photos:
        await callback.answer("Загрузите хотя бы 1 фотографию!", show_alert=True)
        return

    await add_furniture(
        description=data['description'],
        category_name=data['category'],
        country_origin=data['country'],
        kitchen_type=data.get('kitchen_type'),
        photos=photos,
    )

    kb = make_button(admin_kb, sizes=(2, 2, 1, 1))
    await callback.message.edit_text("✅ Товар успешно добавлен в базу данных!", reply_markup=kb)
    await state.clear()
    await callback.answer()