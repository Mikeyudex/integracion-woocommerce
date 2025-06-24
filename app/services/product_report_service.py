from collections import defaultdict
from typing import  Optional
from app.dao.product_log_dao import get_logs_filtered_paginated
from app.services.woocommerce_service import get_product_by_id 
from app.dao.users_dao import get_user_by_id

async def get_product_creation_report(
    page: int = 1,
    limit: int = 20,
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    logs, total = await get_logs_filtered_paginated(
        page=page,
        limit=limit,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )

    grouped = defaultdict(lambda: defaultdict(list))  # user_id -> date -> [logs]

    for log in logs:
        date_str = log["created_at"].strftime("%Y-%m-%d")
        grouped[log["user_id"]][date_str].append(log)

    report_items = []

    user_summary_counts = defaultdict(lambda: {"name": "", "count": 0})
    unique_dates = set()

    for user_id, dates in grouped.items():
        user = await get_user_by_id(user_id)
        if not user:
            continue

        for date_str, logs_on_date in dates.items():
            unique_dates.add(date_str)
            product_summaries = []

            for log in logs_on_date:
                product = await get_product_by_id(log["product_id"])
                if product:
                    product_summaries.append({
                        "id": str(product["id"]),
                        "name": product.get("name", ""),
                        "sku": product.get("sku", ""),
                        "createdAt": product.get("date_created", "")
                    })

            products_created = len(product_summaries)

            report_items.append({
                "id": f"{user_id}-{date_str}",
                "userId": user_id,
                "userName": user.get("nombre", ""),
                "userEmail": user.get("email", ""),
                "date": date_str,
                "productsCreated": products_created,
                "productsList": product_summaries
            })

            user_summary_counts[user_id]["name"] = user.get("nombre", "")
            user_summary_counts[user_id]["count"] += products_created

    # SUMMARY
    total_products = sum(u["count"] for u in user_summary_counts.values())
    total_users = len(user_summary_counts)
    total_days = len(unique_dates)
    average_per_day = round(total_products / total_days, 2) if total_days else 0

    if user_summary_counts:
        most_active_user_id, stats = max(user_summary_counts.items(), key=lambda x: x[1]["count"])
        most_active_user = {
            "id": most_active_user_id,
            "name": stats["name"],
            "totalProducts": stats["count"]
        }
    else:
        most_active_user = {
            "id": "",
            "name": "N/A",
            "totalProducts": 0
        }

    summary = {
        "totalProducts": total_products,
        "totalUsers": total_users,
        "averageProductsPerDay": average_per_day,
        "mostActiveUser": most_active_user,
        "dateRange": {
            "startDate": start_date or "",
            "endDate": end_date or ""
        }
    }

    total_pages = (total + limit - 1) // limit

    return {
        "data": report_items,
        "meta": {
            "currentPage": page,
            "totalPages": total_pages,
            "totalItems": total,
            "itemsPerPage": limit
        },
        "summary": summary
    }