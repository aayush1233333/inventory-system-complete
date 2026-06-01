from sqlalchemy.orm import Session
from typing import Optional
from app.models.models import Customer
from app.schemas.schemas import CustomerCreate, CustomerUpdate


def list_all(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
):
    q = db.query(Customer)
    if search:
        q = q.filter(
            Customer.name.ilike(f"%{search}%") | Customer.email.ilike(f"%{search}%")
        )
    total = q.count()
    items = q.order_by(Customer.name).offset(skip).limit(limit).all()
    return items, total


def get(db: Session, customer_id: int) -> Customer | None:
    return db.query(Customer).filter(Customer.id == customer_id).first()


def get_by_email(db: Session, email: str) -> Customer | None:
    return db.query(Customer).filter(Customer.email == email).first()


def create(db: Session, data: CustomerCreate) -> Customer:
    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update(db: Session, customer: Customer, updates: CustomerUpdate) -> Customer:
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


def delete(db: Session, customer: Customer) -> None:
    db.delete(customer)
    db.commit()
