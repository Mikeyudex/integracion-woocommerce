import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection
from app.configs import Config


MONGO_URI = Config.MONGO_URI
MONGO_DB_NAME = Config.MONGO_DB_NAME

client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[MONGO_DB_NAME]

def get_users_collection() -> Collection:
    return db["users"]

def get_sku_counter_collection() -> Collection:
    return db["sku_counter"]

def get_product_log_collection() -> Collection:
    return db["product_log"]