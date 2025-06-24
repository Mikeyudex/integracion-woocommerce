from fastapi import APIRouter, HTTPException, status
from app.models.user import UserIn, UserOut, UserLogin
from app.dao.users_dao import (
    create_user, get_user_by_email, list_users,
    get_user_by_id, delete_user, update_user
)
from app.utils.auth import verify_password
from app.services.auth_service import create_access_token

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserOut)
async def register(user: UserIn):
    existing = await get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    created = await create_user(user)
    return created

@router.post("/login")
async def login(credentials: UserLogin):
    user = await get_user_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({"sub": user["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/logout")
async def logout():
    return {"message": "Logout exitoso (placeholder)"}

@router.get("/", response_model=list[UserOut])
async def get_all_users():
    return await list_users()

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: str):
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.delete("/{user_id}")
async def delete(user_id: str):
    await delete_user(user_id)
    return {"message": "Usuario eliminado"}

@router.put("/{user_id}", response_model=UserOut)
async def update(user_id: str, data: dict):
    updated = await update_user(user_id, data)
    return updated
