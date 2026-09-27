from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def make_button(buttons: list[tuple[str, str]], sizes: tuple[int, ...] = (2,)) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, callback_data in buttons:
        builder.add(InlineKeyboardButton(text=text, callback_data=callback_data))
    builder.adjust(*sizes)
    return builder.as_markup()