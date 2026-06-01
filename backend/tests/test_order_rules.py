import pytest
from fastapi.testclient import TestClient


def _create_customer(client: TestClient, auth_headers: dict[str, str]) -> int:
    response = client.post(
        "/api/v1/customers/",
        json={
            "name": "Acme Retail",
            "email": "buyer@example.com",
            "phone": "+91 99887 76655",
            "address": "Salt Lake, Kolkata",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_product(
    client: TestClient,
    auth_headers: dict[str, str],
    *,
    sku: str,
    stock_quantity: int,
    price: float = 1200.0,
) -> int:
    response = client.post(
        "/api/v1/products/",
        json={
            "name": f"Product {sku}",
            "sku": sku,
            "description": "Warehouse item",
            "price": price,
            "stock_quantity": stock_quantity,
            "low_stock_threshold": 2,
            "category": "General",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_order_creation_reduces_stock(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    customer_id = _create_customer(client, auth_headers)
    product_id = _create_product(
        client,
        auth_headers,
        sku="SKU-ORDER-001",
        stock_quantity=10,
        price=2500.0,
    )

    order_response = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer_id,
            "notes": "Priority dispatch",
            "items": [{"product_id": product_id, "quantity": 3}],
        },
        headers=auth_headers,
    )

    assert order_response.status_code == 201
    assert order_response.json()["total_amount"] == pytest.approx(7500.0)

    product_response = client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    assert product_response.status_code == 200
    assert product_response.json()["stock_quantity"] == 7


def test_order_creation_rejects_insufficient_stock(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    customer_id = _create_customer(client, auth_headers)
    product_id = _create_product(
        client,
        auth_headers,
        sku="SKU-ORDER-002",
        stock_quantity=2,
    )

    order_response = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 5}],
        },
        headers=auth_headers,
    )

    assert order_response.status_code == 422
    assert "Insufficient stock" in order_response.json()["detail"]

    product_response = client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    assert product_response.status_code == 200
    assert product_response.json()["stock_quantity"] == 2


def test_cancelling_order_restores_stock(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    customer_id = _create_customer(client, auth_headers)
    product_id = _create_product(
        client,
        auth_headers,
        sku="SKU-ORDER-003",
        stock_quantity=8,
    )

    order_response = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": 2}],
        },
        headers=auth_headers,
    )
    assert order_response.status_code == 201

    cancel_response = client.patch(
        f"/api/v1/orders/{order_response.json()['id']}/status",
        json={"status": "cancelled"},
        headers=auth_headers,
    )
    assert cancel_response.status_code == 200

    product_response = client.get(
        f"/api/v1/products/{product_id}",
        headers=auth_headers,
    )
    assert product_response.status_code == 200
    assert product_response.json()["stock_quantity"] == 8
