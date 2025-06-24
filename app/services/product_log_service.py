from app.dao.product_log_dao import log_product_creation, get_products_created_by_user
from datetime import datetime
from typing import Optional

async def save_product_log(product_id: int, user_id: str):
    await log_product_creation(product_id, user_id)

async def get_user_product_report(user_id: str, start: Optional[str] = None, end: Optional[str] = None):
    start_date = datetime.fromisoformat(start) if start else None
    end_date = datetime.fromisoformat(end) if end else None
    return await get_products_created_by_user(user_id, start_date, end_date)
