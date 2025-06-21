from pymongo.collection import Collection
from app.config.db import get_product_log_collection
from datetime import datetime

async def log_product_creation(product_id: int, user_id: str):
    collection: Collection = get_product_log_collection()
    await collection.insert_one({
        "product_id": product_id,
        "user_id": user_id,
        "created_at": datetime.utcnow()
    })

async def get_products_created_by_user(user_id: str, start_date=None, end_date=None):
    collection: Collection = get_product_log_collection()
    
    query = {"user_id": user_id}
    
    if start_date or end_date:
        query["created_at"] = {}
        if start_date:
            query["created_at"]["$gte"] = start_date
        if end_date:
            query["created_at"]["$lte"] = end_date

    cursor = collection.find(query)
    return await cursor.to_list(length=None)
