from database.engine import AsyncSessionLocal
from database.models import User, Category, Furniture, FurniturePhoto, CooperationRequest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def set_user(telegram_id: int, username: str, first_name: str):
    async with AsyncSessionLocal() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        if not user:
            session.add(User(telegram_id=telegram_id, username=username, first_name=first_name))
            await session.commit()


async def get_categories():
    async with AsyncSessionLocal() as session:
        result = await session.scalars(select(Category))
        return result.all()


async def get_category_by_id(category_id: int):
    async with AsyncSessionLocal() as session:
        return await session.get(Category, category_id)


async def add_category(name: str, description: str = None):
    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(Category).where(Category.name == name))
        if existing:
            return False
        session.add(Category(name=name, description=description))
        await session.commit()
        return True


async def add_furniture(
    description: str,
    category_name: str,
    country_origin: str,
    photos: list[str],
    kitchen_type: str | None = None,
):
    async with AsyncSessionLocal() as session:
        item = Furniture(
            description=description,
            category_name=category_name,
            country_origin=country_origin,
            kitchen_type=kitchen_type,
        )
        session.add(item)
        await session.flush()

        for photo_id in photos:
            session.add(FurniturePhoto(furniture_id=item.id, file_path=photo_id))

        await session.commit()
        return item.id


async def delete_furniture_by_id(furniture_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        item = await session.scalar(
            select(Furniture).options(selectinload(Furniture.photos)).where(Furniture.id == furniture_id)
        )
        if not item:
            return False
        await session.delete(item)
        await session.commit()
        return True


async def add_cooperation_request(telegram_id: int, username: str | None, first_name: str | None):
    async with AsyncSessionLocal() as session:
        session.add(CooperationRequest(telegram_id=telegram_id, username=username, first_name=first_name))
        await session.commit()


async def get_cooperation_requests():
    async with AsyncSessionLocal() as session:
        result = await session.scalars(select(CooperationRequest).order_by(CooperationRequest.id.desc()))
        return result.all()


async def get_furniture_by_category(
    category_name: str,
    country_origin: str = None,
    kitchen_type: str = None,
):
    async with AsyncSessionLocal() as session:
        query = select(Furniture).options(selectinload(Furniture.photos)).where(Furniture.category_name == category_name)
        if country_origin:
            query = query.where(Furniture.country_origin == country_origin)
        if kitchen_type:
            query = query.where(Furniture.kitchen_type == kitchen_type)
        result = await session.scalars(query)
        return result.unique().all()