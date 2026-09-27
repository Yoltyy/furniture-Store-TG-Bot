from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from database.engine import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(64), nullable=True)
    first_name = Column(String(64), nullable=True)
    registration_date = Column(DateTime, server_default=func.now())
    is_admin = Column(Boolean, default=False)


class Furniture(Base):
    __tablename__ = 'furniture'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    country_origin = Column(String(100), nullable=False)
    kitchen_type = Column(String(50), nullable=True)

    photos = relationship("FurniturePhoto", back_populates="furniture", cascade="all, delete-orphan")


class FurniturePhoto(Base):
    __tablename__ = 'furniture_photos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    furniture_id = Column(Integer, ForeignKey('furniture.id', ondelete='CASCADE'), nullable=False)
    file_path = Column(Text, nullable=False)

    furniture = relationship("Furniture", back_populates="photos")


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)


class CooperationRequest(Base):
    __tablename__ = 'cooperation_requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(64), nullable=True)
    first_name = Column(String(64), nullable=True)
    created_at = Column(DateTime, server_default=func.now())