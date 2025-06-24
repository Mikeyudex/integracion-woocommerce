from typing import List, Tuple, Optional
from datetime import datetime, timedelta, timezone
from pymongo.collection import Collection
from app.config.db import get_product_log_collection


async def log_product_creation(product_id: int, user_id: str):
    collection: Collection = get_product_log_collection()
    await collection.insert_one({
        "product_id": product_id,
        "user_id": user_id,
        "created_at": datetime.now(timezone.utc) - timedelta(hours=5)
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

async def get_logs_filtered_paginated(
    page: int = 1,
    limit: int = 20,
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Tuple[List[dict], int]:
    collection: Collection = get_product_log_collection()
    query = {}

    if user_id:
        query["user_id"] = user_id

    if start_date or end_date:
        date_filter = {}
        if start_date:
            try:
                date_filter["$gte"] = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid start_date format. Use YYYY-MM-DD.")
        if end_date:
            try:
                date_filter["$lte"] = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid end_date format. Use YYYY-MM-DD.")
        query["created_at"] = date_filter

    total = await collection.count_documents(query)

    cursor = (
        collection.find(query)
        .sort("created_at", -1)
        .skip((page - 1) * limit)
        .limit(limit)
    )

    logs = [log async for log in cursor]

    return logs, total