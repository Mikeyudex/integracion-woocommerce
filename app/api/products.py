from fastapi import APIRouter, Depends, Query
from ..services.auth_service import verify_token
from ..services.woocommerce_service import get_all_products, create_product
from ..models.product import Product
from typing import List

router = APIRouter()

@router.get("/products")
def fetch_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    user=Depends(verify_token)
):
    return get_all_products(page=page, per_page=limit)

@router.post("/products")
def add_product(product: Product, user=Depends(verify_token)):
    # Transforma Product (Pydantic) a dict que WooCommerce acepta
    wc_product = {
        "name": product.name,
        "type": "simple",
        "regular_price": str(product.price),
        "description": product.description,
    }
    return create_product(wc_product)
