import warnings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.routers import products, customers, orders, dashboard, auth

settings = get_settings()

# Warn loudly about insecure defaults at startup
if settings.SECRET_KEY == "changeme-in-production":
    warnings.warn(
        "⚠️  SECRET_KEY is set to the default insecure value. "
        "Set a strong SECRET_KEY in your .env before deploying.",
        stacklevel=1,
    )

app = FastAPI(
    title="StockFlow — Inventory & Order Management API",
    description="Full-stack inventory and order management system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS — only explicitly configured origins are allowed
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,   # fixed: removed wildcard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "StockFlow API", "docs": "/api/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}
