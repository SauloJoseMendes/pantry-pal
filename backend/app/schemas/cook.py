from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class CookCreate(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=100)


class Cook(BaseModel):
    cook_id: int
    username: str
    email: EmailStr
    display_name: str | None
    created_at: datetime


class CookCredentials(BaseModel):
    cook_id: int
    username: str
    password_hash: str
