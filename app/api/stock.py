from fastapi import APIRouter, Depends
from ..services.auth_service import verify_token
from ..services.woocommerce_service import update_stock_quantity

router = APIRouter()

@router.put("/stock/{product_id}")
def update_stock(product_id: int, quantity: int, user=Depends(verify_token)):
    return update_stock_quantity(product_id, quantity)
