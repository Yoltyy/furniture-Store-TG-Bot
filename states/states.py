from aiogram.fsm.state import StatesGroup, State

class AddCategoryState(StatesGroup):
    name = State()
    description = State()

class AddFurnitureState(StatesGroup):
    category = State()
    type_or_country = State()
    description = State()
    photos = State()

class RemoveFurnitureState(StatesGroup):
    furniture_id = State()