from woocommerce import API
from typing import List, Dict, Any
from app.configs import Config
from app.dao.sku_counter_dao import increment_sku_counter
from app.services.product_log_service import save_product_log


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

async def create_product(product_data: dict, user_id: str):
    try:
        response = wcapi.post("products", data=product_data)
        response_data = response.json()

        # Manejar errores de la API de WooCommerce
        if response.status_code >= 400:
            return {
                "error": response_data.get("message", "Error desconocido al crear producto"),
                "code": response_data.get("code"),
                "status": response.status_code,
                "data": response_data.get("data")
            }
        # Validar creación correcta
        if "id" in response_data:
            await increment_sku_counter()
            await save_product_log(response_data["id"], user_id)
            return response_data
        else:
            return {
                "error": "Respuesta inesperada al crear producto",
                "response": response_data
            }

    except Exception as e:
        print("Excepción al crear producto:", e)
        return {"error": "Error interno al crear producto", "detail": str(e)}

async def get_product_by_id(product_id: int):
    response = wcapi.get(f"products/{product_id}")
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()

def update_product(product_id: int, product_data: dict):
    response = wcapi.put(f"products/{product_id}", data=product_data)
    return response.json()

def delete_product(product_id: int):
    response = wcapi.delete(f"products/{product_id}", params={"force": True})
    return response.json()

def get_last_sku_consecutive():
    page = 1
    per_page = 100
    max_sku_number = 0

    while True:
        response = wcapi.get("products", params={"page": page, "per_page": per_page})
        products = response.json()

        if not products:
            break

        for product in products:
            sku = product.get("sku")
            if sku and sku.isdigit():
                sku_num = int(sku)
                if sku_num > max_sku_number:
                    max_sku_number = sku_num

        if len(products) < per_page:
            break
        page += 1

    next_sku = str(max_sku_number + 1)

    return {
        "last_sku": str(max_sku_number),
        "next_sku": next_sku
    }

# ------------------- Categorías -------------------

def get_all_categories_paginated(page: int = 1, per_page: int = 10):
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

def get_categories() -> List[Dict[str, Any]]:
    all_categories = []
    page = 1

    while True:
        response = wcapi.get("products/categories", params={
            "per_page": 100,
            "page": page,
            "hide_empty": False  # incluir categorías vacías también
        })
        response.raise_for_status()

        data = response.json()
        if not data:
            break

        all_categories.extend(data)
        page += 1

    return all_categories

def build_category_tree(categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    category_map = {cat["id"]: {**cat, "children": []} for cat in categories}
    tree = []

    for cat in categories:
        parent_id = cat["parent"]
        if parent_id and parent_id in category_map:
            category_map[parent_id]["children"].append(category_map[cat["id"]])
        else:
            tree.append(category_map[cat["id"]])
    
    return tree

def flatten_category_tree(tree: List[Dict[str, Any]], depth: int = 0) -> List[Dict[str, Any]]:
    flattened = []
    prefix = "— " * depth

    for category in tree:
        flattened.append({
            "label": f"{prefix}{category['name']}",
            "value": category["slug"],
            "id": category["id"],
            "slug": category["slug"],
            "parent": category["parent"]
        })
        if category.get("children"):
            flattened.extend(flatten_category_tree(category["children"], depth + 1))
    
    return flattened

def create_category(category_data: dict):
    return wcapi.post("products/categories", data=category_data).json()

def update_category(category_id: int, category_data: dict):
    return wcapi.put(f"products/categories/{category_id}", data=category_data).json()

def delete_category(category_id: int):
    return wcapi.delete(f"products/categories/{category_id}", params={"force": True}).json()

# ------------------- Stock -------------------

def update_stock_quantity(product_id: int, quantity: int):
    return wcapi.put(f"products/{product_id}", data={"stock_quantity": quantity}).json()
