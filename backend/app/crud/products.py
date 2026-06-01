from sqlalchemy.orm import Session
from typing import Optional
from app.models.models import Product
from app.schemas.schemas import ProductCreate, ProductUpdate


def list_all(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    low_stock: bool = False,
):
    q = db.query(Product)
    if search:
        q = q.filter(
            Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%")
        )
    if low_stock:
        q = q.filter(Product.stock_quantity <= Product.low_stock_threshold)
    total = q.count()
    items = q.order_by(Product.name).offset(skip).limit(limit).all()
    return items, total


def get(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def get_by_sku(db: Session, sku: str) -> Product | None:
    return db.query(Product).filter(Product.sku == sku).first()


def create(db: Session, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update(db: Session, product: Product, updates: ProductUpdate) -> Product:
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete(db: Session, product: Product) -> None:
    db.delete(product)
    db.commit()
