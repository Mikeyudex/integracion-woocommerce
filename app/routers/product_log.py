from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.services.product_log_service import get_user_product_report
from app.models.product_log import ProductLogOut
from app.services.auth_service import verify_token

router = APIRouter(prefix="/logs", tags=["product-logs"])

@router.get("/user", response_model=List[ProductLogOut])
async def fetch_user_product_logs(
    user_id: str = Query(...),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    user=Depends(verify_token)
):
    return await get_user_product_report(user_id=user_id, start=start, end=end)
