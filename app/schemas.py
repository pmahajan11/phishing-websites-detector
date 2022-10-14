from pydantic import BaseModel, EmailStr
from typing import Union
from datetime import datetime


# Request Models

class UserIn(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

class APIKeyIn(BaseModel):
    email: EmailStr
    password: str


class Query(BaseModel):
    api_key: str
    query: str

# ===============================================================================

# Response Models

class NewUserOut(BaseModel):
    email: EmailStr
    created_at: datetime
    api_key: str
    usage_count: int
    last_used_at: datetime


class UserOut(BaseModel):
    email: EmailStr
    created_at: datetime
    usage_count: int
    last_used_at: datetime


class APIKeyOut(BaseModel):
    email: EmailStr
    api_key: str


class Prediction(BaseModel):
    email: EmailStr
    prediction: dict
    usage_count: int
    last_used_at: datetime