from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy import create_engine
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'
    pk = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(63))
    description = Column(String(255))
    image = Column(String, nullable=True)
    private = Column(Boolean, default=False)


class User(Base):
    __tablename__ = 'users'
    pk = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    email = Column(String(63))
    password = Column(String(63))
    first_name = Column(String(63))
    last_name = Column(String(63))
    token = Column(String(127))
    ip_address = Column(String(15))
    __table_args__ = (
        UniqueConstraint('email', name='_email'),
    )

