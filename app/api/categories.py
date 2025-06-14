from fastapi import APIRouter, Depends, Query
from ..services.auth_service import verify_token
from ..services.woocommerce_service import (
    get_all_categories, create_category, update_category, delete_category
)

router = APIRouter()

@router.get("/categories")
def list_categories(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    user=Depends(verify_token)):
    return get_all_categories(page=page, per_page=limit)

@router.post("/categories")
def add_category(category: dict, user=Depends(verify_token)):
    return create_category(category)

@router.put("/categories/{category_id}")
def modify_category(category_id: int, category: dict, user=Depends(verify_token)):
    return update_category(category_id, category)

@router.delete("/categories/{category_id}")
def remove_category(category_id: int, user=Depends(verify_token)):
    return delete_category(category_id)
