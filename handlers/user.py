from aiogram.types import URLInputFile
from aiogram import Router, F

from aiogram.filters import CommandStart
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

from keyboard.keyboard_builder import make_button
from database.requests import (
    set_user,
    get_categories,
    get_category_by_id,
    get_furniture_by_category,
    add_cooperation_request,
)

router = Router()

KITCHEN_KEYWORD = "кухон"


WELCOME_TEXT = (
    "👋 <b>Добро пожаловать в наш мебельный бот!</b>\n\n"
    "🔹 Здесь вы найдете отличную и качественную мебель для любого интерьера.\n\n"
    "💡 <b>Как сделать заказ:</b>\n"
    "1. Выберите категорию мебели\n"
    "2. Просмотрите варианты\n"
    "3. Свяжитесь с менеджером для заказа\n\n"
    "📲 Для оформления заказа или консультации нажмите соответствующую кнопку.\n"
    "В любой момент можно вернуться в главное меню.\n\n"
    "👇 <b>Выберите категорию из меню ниже:</b>"
)


def get_input_file(path: str):
    if path.startswith("http://") or path.startswith("https://"):
        return URLInputFile(path)
    return path


async def build_categories_keyboard():
    categories = await get_categories()
    buttons = [(cat.name, f"browse_cat_{cat.id}") for cat in categories]
    buttons.append(("ℹ️ О компании / Контакты", "about_company"))
    buttons.append(("🤝 Сотрудничество", "cooperation_company"))
    return make_button(buttons, sizes=(2,)), categories


@router.message(CommandStart())
async def cmd_start(message: Message):
    await set_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    kb, categories = await build_categories_keyboard()
    if not categories:
        await message.answer(
            "👋 Добро пожаловать! Пока в каталоге нет ни одной категории мебели.\n"
            "Загляните позже — мы скоро добавим товары.",
        )
        return

    await message.answer(WELCOME_TEXT, reply_markup=kb, parse_mode="HTML")


@router.message(Command("admin_panel"))
async def admin_panel_denied(message: Message):
    await message.answer("⛔ У вас нет доступа к админской панели.")


@router.callback_query(F.data == "about_company")
async def about_company_cmd(callback: CallbackQuery):
    about_text = (
        "ℹ️ <b>О нашей компании:</b>\n\n"
        "Мы создаем и поставляем качественную и современную мебель для вашего дома и офиса уже более 10 лет.\n\n"
        "📍 <b>Наши контакты:</b>\n"
        "• <b>Адрес:</b> г. Грозный, ул. Мебельная, д. 15\n"
        "• <b>Телефон:</b> +7 (995) 333-44-56\n"
        "• <b>График работы:</b> Пн-Вс с 09:00 до 20:00\n\n"
        "📲 <b>Соцсети и связи:</b>\n"
        '• WhatsApp: <a href="https://wa.me/79953334456">Написать в WhatsApp</a>\n'
        "• Telegram: @suleymanovv076\n"
    )

    back_kb = make_button([("⬅️ Назад в меню", "back_to_main")], sizes=(1,))
    await callback.message.answer(about_text, reply_markup=back_kb, parse_mode="HTML", disable_web_page_preview=True)
    await callback.answer()


@router.callback_query(F.data == "cooperation_company")
async def cooperation_cmd(callback: CallbackQuery):
    await add_cooperation_request(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
    )

    coop_text = (
        "🤝 <b>Сотрудничество:</b>\n\n"
        "Мы всегда открыты для новых партнерств!\n\n"
        "💼 <b>Приглашаем к сотрудничеству:</b>\n"
        "• Дизайнеров интерьера\n"
        "• Архитекторов\n"
        "• Оптовых покупателей и региональных дилеров\n"
        "• Поставщиков материалов и фурнитуры\n\n"
        "📧 <b>Коммерческие предложения отправляйте на почту:</b>\n"
        "ansarium@mail.ru или менеджеру: @suleymanovv076"
    )

    back_kb = make_button([("⬅️ Назад в меню", "back_to_main")], sizes=(1,))
    await callback.message.answer(coop_text, reply_markup=back_kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    kb, categories = await build_categories_keyboard()
    if not categories:
        await callback.message.answer("Пока в каталоге нет ни одной категории мебели.")
        await callback.answer()
        return

    await callback.message.answer(WELCOME_TEXT, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("browse_cat_"))
async def select_category(callback: CallbackQuery):
    category_id = callback.data.replace("browse_cat_", "")
    category = await get_category_by_id(int(category_id))

    if not category:
        await callback.answer("⚠️ Категория не найдена.", show_alert=True)
        return

    is_kitchen = KITCHEN_KEYWORD in category.name.lower()

    if is_kitchen:
        kb = make_button(
            [
                ("📐 Прямая кухня", f"browse_kitchen_{category.id}_straight"),
                ("📏 Угловая кухня", f"browse_kitchen_{category.id}_corner"),
                ("⬅️ Назад", "back_to_main"),
            ],
            sizes=(1, 1, 1),
        )
        text = "Отлично! Теперь выберите тип кухни:"
    else:
        kb = make_button(
            [
                ("🇷🇺 Россия", f"browse_country_{category.id}_ru"),
                ("🇹🇷 Турция", f"browse_country_{category.id}_tr"),
                ("⬅️ Назад", "back_to_main"),
            ],
            sizes=(1, 1, 1),
        )
        text = "Отлично! Теперь выберите страну производства:"

    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("browse_country_"))
async def show_products_by_country(callback: CallbackQuery):
    _, _, category_id, country_code = callback.data.split("_")
    country_map = {"ru": "Россия", "tr": "Турция"}
    country = country_map.get(country_code)

    category = await get_category_by_id(int(category_id))
    if not category:
        await callback.answer("⚠️ Категория не найдена.", show_alert=True)
        return

    products = await get_furniture_by_category(category_name=category.name, country_origin=country)
    await send_products(callback, category.name, products)


@router.callback_query(F.data.startswith("browse_kitchen_"))
async def show_products_by_kitchen_type(callback: CallbackQuery):
    _, _, category_id, type_code = callback.data.split("_")
    type_map = {"straight": "Прямая кухня", "corner": "Угловая кухня"}
    kitchen_type = type_map.get(type_code)

    category = await get_category_by_id(int(category_id))
    if not category:
        await callback.answer("⚠️ Категория не найдена.", show_alert=True)
        return

    products = await get_furniture_by_category(category_name=category.name, kitchen_type=kitchen_type)
    await send_products(callback, category.name, products)


async def send_products(callback: CallbackQuery, category_name: str, products):
    if not products:
        await callback.message.answer(f"⚠️ В категории «{category_name}» пока нет товаров.")
        await callback.answer()
        return

    total = len(products)

    for idx, item in enumerate(products, 1):
        caption_text = (
            f"📌 <b>{category_name}</b>\n\n"
            f"{item.description}\n\n"
            f"• <b>Страна производства:</b> {item.country_origin}\n\n"
            f"📲 <b>Для заказа этой мебели:</b>\n"
            f'WhatsApp: <a href="https://wa.me/79256770404">https://wa.me/79256770404</a>\n\n'
            f"✨ Подписывайтесь на наш Instagram и будьте в курсе новинок!\n\n"
            f"<i>Показано {idx} из {total} товаров в категории.</i>"
        )

        photos = getattr(item, "photos", None)

        if photos:
            if len(photos) == 1:
                await callback.message.answer_photo(
                    photo=get_input_file(photos[0].file_path),
                    caption=caption_text,
                    parse_mode="HTML",
                )
            else:
                media = []
                for p_idx, photo_obj in enumerate(photos):
                    file_input = get_input_file(photo_obj.file_path)
                    if p_idx == 0:
                        media.append(InputMediaPhoto(media=file_input, caption=caption_text, parse_mode="HTML"))
                    else:
                        media.append(InputMediaPhoto(media=file_input))

                await callback.message.answer_media_group(media=media)
        else:
            await callback.message.answer(caption_text, parse_mode="HTML")

    await callback.answer()