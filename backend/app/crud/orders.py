from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.models.models import Order, OrderItem, Product, Customer, OrderStatus


def list_all(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[OrderStatus] = None,
    customer_id: Optional[int] = None,
):
    q = db.query(Order).options(
        joinedload(Order.customer),
        joinedload(Order.items).joinedload(OrderItem.product),
    )
    if status_filter:
        q = q.filter(Order.status == status_filter)
    if customer_id:
        q = q.filter(Order.customer_id == customer_id)
    total = q.count()
    items = q.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return items, total


def get(db: Session, order_id: int) -> Order | None:
    return (
        db.query(Order)
        .options(
            joinedload(Order.customer),
            joinedload(Order.items).joinedload(OrderItem.product),
        )
        .filter(Order.id == order_id)
        .first()
    )


def _reload_with_relations(db: Session, order_id: int) -> Order:
    return (
        db.query(Order)
        .options(
            joinedload(Order.customer),
            joinedload(Order.items).joinedload(OrderItem.product),
        )
        .filter(Order.id == order_id)
        .first()
    )


def create(db: Session, customer_id: int, items_data: list, notes: Optional[str]) -> Order:
    items_to_create = []
    total_amount = 0.0

    for item in items_data:
        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .with_for_update()
            .first()
        )
        if not product:
            raise ValueError(f"Product ID {item.product_id} not found")
        if product.stock_quantity < item.quantity:
            raise ValueError(
                f"Insufficient stock for '{product.name}' (SKU: {product.sku}). "
                f"Requested: {item.quantity}, Available: {product.stock_quantity}"
            )
        product.stock_quantity -= item.quantity
        total_amount += product.price * item.quantity
        items_to_create.append(
            OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
            )
        )

    order = Order(
        customer_id=customer_id,
        total_amount=total_amount,
        notes=notes,
        status=OrderStatus.PENDING,
    )
    db.add(order)
    db.flush()

    for item in items_to_create:
        item.order_id = order.id
        db.add(item)

    db.commit()
    return _reload_with_relations(db, order.id)


def update_status(db: Session, order: Order, new_status: OrderStatus) -> Order:
    if new_status == OrderStatus.CANCELLED and order.status != OrderStatus.CANCELLED:
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock_quantity += item.quantity
    order.status = new_status
    db.commit()
    return _reload_with_relations(db, order.id)


def delete(db: Session, order: Order) -> None:
    if order.status != OrderStatus.CANCELLED:
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock_quantity += item.quantity
    db.delete(order)
    db.commit()
