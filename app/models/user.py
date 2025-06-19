from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserIn(BaseModel):
    email: EmailStr
    documento: str
    password: str
    nombre: str
    apellido: str
    rol: str

class UserOut(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    documento: str
    nombre: str
    apellido: str
    rol: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
