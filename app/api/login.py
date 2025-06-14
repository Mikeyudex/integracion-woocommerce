from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from ..services.auth_service import create_access_token
from app.configs import Config

router = APIRouter()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != Config.USERNAME_MOCKUP_USER or form_data.password != Config.PASSWORD_MOCKUP_USER:
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}
