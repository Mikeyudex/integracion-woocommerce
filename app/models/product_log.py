from pydantic import BaseModel
from datetime import datetime

class ProductLogOut(BaseModel):
    product_id: int
    user_id: str
    created_at: datetime