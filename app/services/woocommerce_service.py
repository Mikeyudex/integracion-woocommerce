from woocommerce import API
from app.configs import Config


wcapi = API(
    url=Config.WC_URL, 
    consumer_key=Config.WC_KEY,
    consumer_secret=Config.WC_SECRET,
    version="wc/v3",
    timeout=10
)

# ------------------- Productos -------------------

def get_all_products(page: int = 1, per_page: int = 10):
    params = {
        "page": page,
        "per_page": per_page
    }
    response = wcapi.get("products", params=params)
    return {
        "products": response.json(),
        "pagination": {
            "total_items": int(response.headers.get("X-WP-Total", 0)),
            "total_pages": int(response.headers.get("X-WP-TotalPages", 0)),
            "current_page": page,
            "per_page": per_page
        }
    }

def create_product(product_data: dict):
    response = wcapi.post("products", data=product_data)
    return response.json()

def update_product(product_id: int, product_data: dict):
    response = wcapi.put(f"products/{product_id}", data=product_data)
    return response.json()

def delete_product(product_id: int):
    response = wcapi.delete(f"products/{product_id}", params={"force": True})
    return response.json()

# ------------------- Categorías -------------------

def get_all_categories(page: int = 1, per_page: int = 10):
    params = {
        "page": page,
        "per_page": per_page
    }
    response = wcapi.get("products/categories", params=params)
    return {
        "categories": response.json(),
        "pagination": {
            "total_items": int(response.headers.get("X-WP-Total", 0)),
            "total_pages": int(response.headers.get("X-WP-TotalPages", 0)),
            "current_page": page,
            "per_page": per_page
        }
    }

def create_category(category_data: dict):
    return wcapi.post("products/categories", data=category_data).json()

def update_category(category_id: int, category_data: dict):
    return wcapi.put(f"products/categories/{category_id}", data=category_data).json()

def delete_category(category_id: int):
    return wcapi.delete(f"products/categories/{category_id}", params={"force": True}).json()

# ------------------- Stock -------------------

def update_stock_quantity(product_id: int, quantity: int):
    return wcapi.put(f"products/{product_id}", data={"stock_quantity": quantity}).json()
