from pydantic import BaseModel

class Product(BaseModel):
    sku: str
    name: str
    slug: str
    regular_price: str
    description: str
    stock_quantity: int
    categories: list[dict]
    tags: list[dict]
    images: list[dict]
    manage_stock: bool
    meta_data: list[dict]
    user_id: str = None