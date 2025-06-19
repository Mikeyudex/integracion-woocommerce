from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection
from app.configs import Config


MONGO_URI = Config.MONGO_URI
MONGO_DB_NAME = Config.MONGO_DB_NAME

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]

def get_users_collection() -> Collection:
    return db["users"]
