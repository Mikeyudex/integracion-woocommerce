from bson import ObjectId
from ..config.db import get_users_collection
from ..models.user import UserIn
from ..utils.auth import hash_password

async def create_user(user: UserIn) -> dict:
    user_data = user.dict()
    user_data["password"] = hash_password(user.password)
    result = await get_users_collection().insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)
    return user_data

async def get_user_by_email(email: str) -> dict:
    user = await get_users_collection().find_one({"email": email})
    user_map = dict(user, _id=str(user["_id"]))
    return user_map

async def get_user_by_id(user_id: str) -> dict:
    user = await get_users_collection().find_one({"_id": ObjectId(user_id)})
    user_map = dict(user, _id=str(user["_id"]))
    return user_map

async def list_users():
    users_cursor = get_users_collection().find()
    return [dict(u, _id=str(u["_id"])) async for u in users_cursor]

async def delete_user(user_id: str):
    return await get_users_collection().delete_one({"_id": ObjectId(user_id)})

async def update_user(user_id: str, data: dict):
    if "password" in data:
        data["password"] = hash_password(data["password"])
    await get_users_collection().update_one({"_id": ObjectId(user_id)}, {"$set": data})
    return await get_user_by_id(user_id)
