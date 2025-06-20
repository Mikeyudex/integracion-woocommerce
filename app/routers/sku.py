from fastapi import APIRouter, Depends
from app.dao.sku_counter_dao import get_current_sku
from app.services.auth_service import verify_token

router = APIRouter(prefix="/sku", tags=["SKU"])

@router.get("/next")
async def get_next_sku(user=Depends(verify_token)):
    current_sku = await get_current_sku()
    next_sku = current_sku + 1
    return {"next_sku": next_sku}