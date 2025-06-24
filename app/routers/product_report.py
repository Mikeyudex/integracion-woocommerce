from fastapi import APIRouter, Query
from typing import Optional
from app.services.product_report_service import get_product_creation_report
from app.models.product_report import ReportResponse

router = APIRouter(prefix="/reports", tags=["product-reports"])

@router.get("/products", response_model=ReportResponse)
async def product_creation_report(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    userId: Optional[str] = None,
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
):
    result = await get_product_creation_report(
        page=page,
        limit=limit,
        user_id=userId,
        start_date=startDate,
        end_date=endDate,
    )

    return result