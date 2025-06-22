from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.products import router as products_router
from .api.categories import router as categories_router
from .api.stock import router as stock_router
from .api.login import router as login_router
from .routers.users import router as users_router
from .routers.sku import router as sku_routes
from .routers.media import router as media_router
from .routers.product_report import router as product_report_router


app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # En producción, especificar dominios permitidos
    allow_credentials=True,  # Cambiar a True para MCP
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
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
