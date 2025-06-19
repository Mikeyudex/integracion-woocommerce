import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PORT = os.getenv('PORT')
    ENV = os.getenv('ENV')
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    JWT_SECRET = os.getenv("JWT_SECRET", "jwt_secret_key")
    JWT_EXPIRATION = os.getenv("JWT_EXPIRATION", 3600)
    PASSWORD_MOCKUP_USER = os.getenv("PASSWORD_MOCKUP_USER", "password")
    USERNAME_MOCKUP_USER = os.getenv("USERNAME_MOCKUP_USER", "username")
    WC_URL = os.getenv("WC_URL", "")
    WC_KEY = os.getenv("WC_KEY", "")
    WC_SECRET = os.getenv("WC_SECRET", "")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "myapp")
    
    @staticmethod
    def get_config(key):
        return getattr(Config, key)
    