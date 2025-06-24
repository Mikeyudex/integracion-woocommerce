from pymongo.collection import Collection
from app.config.db import get_sku_counter_collection

async def get_current_sku() -> int:
    collection: Collection = get_sku_counter_collection()
    doc = await collection.find_one({"_id": "sku"})
    if doc and "seq" in doc:
        return doc["seq"]
    return 19999  # valor inicial - 1


async def increment_sku_counter() -> int:
    collection = get_sku_counter_collection()
    result = await collection.find_one_and_update(
        {"_id": "sku"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    return result["seq"]