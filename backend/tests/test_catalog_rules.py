from fastapi.testclient import TestClient


def test_duplicate_product_sku_is_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    payload = {
        "name": "Laptop",
        "sku": "LAP-001",
        "description": "15-inch business laptop",
        "price": 49999.0,
        "stock_quantity": 12,
        "low_stock_threshold": 3,
        "category": "Electronics",
    }

    first_response = client.post(
        "/api/v1/products/",
        json=payload,
        headers=auth_headers,
    )
    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/api/v1/products/",
        json={**payload, "name": "Backup Laptop"},
        headers=auth_headers,
    )
    assert duplicate_response.status_code == 409
    assert "SKU" in duplicate_response.json()["detail"]


def test_duplicate_customer_email_is_rejected(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    payload = {
        "name": "Priya Sharma",
        "email": "priya@example.com",
        "phone": "+91 98765 43210",
        "address": "MG Road, Bengaluru",
    }

    first_response = client.post(
        "/api/v1/customers/",
        json=payload,
        headers=auth_headers,
    )
    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/api/v1/customers/",
        json={**payload, "name": "Priya S."},
        headers=auth_headers,
    )
    assert duplicate_response.status_code == 409
    assert "email" in duplicate_response.json()["detail"].lower()
