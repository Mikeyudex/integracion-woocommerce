from fastapi import APIRouter, Depends, Query
from typing import List, Dict, Any
from ..services.auth_service import verify_token
from ..services.woocommerce_service import (
    get_all_categories_paginated,
    create_category,
    update_category,
    delete_category,
    get_categories,
    build_category_tree
)

router = APIRouter()

@router.get("/categories-paginated")
def list_categories_paginated(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    user=Depends(verify_token)):
    return get_all_categories_paginated(page=page, per_page=limit)

@router.get("/categories-tree", response_model=List[Dict[str, Any]])
def list_categories(user=Depends(verify_token)):
    """
    Devuelve las categorías jerárquicamente organizadas desde WooCommerce.
    """
    categories = get_categories()
    tree = build_category_tree(categories)
    return tree

@router.post("/categories")
def add_category(category: dict, user=Depends(verify_token)):
    return create_category(category)

@router.put("/categories/{category_id}")
def modify_category(category_id: int, category: dict, user=Depends(verify_token)):
    return update_category(category_id, category)

@router.delete("/categories/{category_id}")
def remove_category(category_id: int, user=Depends(verify_token)):
    return delete_category(category_id)
