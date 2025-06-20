from fastapi import APIRouter
from app.dao.sku_counter_dao import get_current_sku

router = APIRouter(prefix="/sku", tags=["SKU"])

@router.get("/next")
async def get_next_sku():
    current_sku = get_current_sku()
    next_sku = current_sku + 1
    return {"next_sku": next_sku}