from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.products import router as products_router
from app.api.categories import router as categories_router
from app.api.stock import router as stock_router
from app.api.login import router as login_router
from app.routers.users import router as users_router
from app.routers.sku import router as sku_routes
from app.routers.media import router as media_router
from app.routers.product_report import router as product_report_router


app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://erp.totalmotors.cl"],  # En producción, especificar dominios permitidos
    allow_credentials=True,  # Cambiar a True para MCP
    allow_methods=["GET", "POST", "OPTIONS", "HEAD", "PUT", "DELETE"],
    allow_headers=[
        "Content-Type",
        "Authorization", 
        "X-Requested-With",
        "Accept",
        "Origin",
        "User-Agent",
        "Cache-Control"
    ],
    expose_headers=["*"]
)

app.include_router(login_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(categories_router, prefix="/api")
app.include_router(stock_router, prefix="/api")
app.include_router(users_router)
app.include_router(sku_routes)
app.include_router(media_router)
app.include_router(product_report_router)
