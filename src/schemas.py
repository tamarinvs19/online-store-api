from typing import Optional

from ipaddress import IPv4Address
from pydantic import BaseModel, Field


class Product(BaseModel):
    pk: int
    name: str = Field(max_length=63)
    description: str = Field(max_length=255)
    image: Optional[str]

    class Config:
        orm_mode = True


class User(BaseModel):
    email: str = Field(max_length=63)
    first_name: str = Field(max_length=63)
    last_name: str = Field(max_length=63)
    token: str = Field(max_length=127)

    class Config:
        orm_mode = True

