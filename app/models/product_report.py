from pydantic import BaseModel
from typing import List
from datetime import datetime

class ProductSummary(BaseModel):
    id: str
    name: str
    sku: str
    createdAt: datetime

class ProductCreationReport(BaseModel):
    id: str
    userId: str
    userName: str
    userEmail: str
    date: str  # YYYY-MM-DD
    productsCreated: int
    productsList: List[ProductSummary]

class ReportMeta(BaseModel):
    currentPage: int
    totalPages: int
    totalItems: int
    itemsPerPage: int

class ReportSummary(BaseModel):
    totalProducts: int
    totalUsers: int
    averageProductsPerDay: float
    mostActiveUser: dict  # Should contain id, name, totalProducts
    dateRange: dict  # Should contain startDate and endDate as strings

class ReportResponse(BaseModel):
    data: List[ProductCreationReport]
    meta: ReportMeta
    summary: ReportSummary
