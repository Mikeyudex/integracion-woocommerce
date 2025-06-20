from fastapi import APIRouter, Depends, Query,HTTPException, status
from fastapi.responses import JSONResponse
import json
from ..services.auth_service import verify_token
from ..services.woocommerce_service import get_all_products, create_product, get_last_sku_consecutive
from ..models.product import Product
from typing import List
from pydantic import ValidationError

router = APIRouter()

@router.get("/products")
def fetch_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    user=Depends(verify_token)
):
    return get_all_products(page=page, per_page=limit)

@router.post("/products")
async def add_product(product: Product, user=Depends(verify_token)):
    try:
        product_data = product.model_dump()
        result = await create_product(product_data)
        if "error" in result:
            return JSONResponse(
                status_code=result.get("status", 400),
                content=result
            )
        return result
    except ValidationError as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Error de validación",
                "detail": e.errors()
            }
        )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Error creando producto",
                "detail": str(e)
            }
        )

@router.get("/products/next-sku")
def get_next_numeric_sku(user=Depends(verify_token)):
    return get_last_sku_consecutive()