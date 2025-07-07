from fastapi import APIRouter, Depends
from app.dao.sku_counter_dao import get_current_sku, update_sku_sequence
from app.services.auth_service import verify_token

router = APIRouter(prefix="/sku", tags=["SKU"])

@router.get("/next")
async def get_next_sku(user=Depends(verify_token)):
    current_sku = await get_current_sku()
    next_sku = current_sku + 1
    return {"next_sku": next_sku}

@router.put("/update-sequence/{new_sequence}")
async def update_sequence(new_sequence: int, user=Depends(verify_token)):
    if new_sequence <= 0:
        return {"message": "Invalid sequence number"}
    print(new_sequence)
    await update_sku_sequence(new_sequence)
    return {"message": "Sequence updated successfully"}