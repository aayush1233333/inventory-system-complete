from fastapi.testclient import TestClient


def test_dashboard_stats_include_catalog_and_order_totals(
    client: TestClient,
) -> None:
    customer = client.post(
        "/customers",
        json={
            "name": "Dashboard Customer",
            "email": "dashboard@example.com",
            "phone": "+91 90000 00001",
            "address": "Dashboard test",
        },
    )
    assert customer.status_code == 201

    stocked_product = client.post(
        "/products",
        json={
            "name": "Stocked Product",
            "sku": "DASH-STOCKED",
            "price": 100.0,
            "stock_quantity": 10,
            "low_stock_threshold": 2,
        },
    )
    assert stocked_product.status_code == 201

    low_stock_product = client.post(
        "/products",
        json={
            "name": "Low Stock Product",
            "sku": "DASH-LOW",
            "price": 50.0,
            "stock_quantity": 1,
            "low_stock_threshold": 2,
        },
    )
    assert low_stock_product.status_code == 201

    order = client.post(
        "/orders",
        json={
            "customer_id": customer.json()["id"],
            "items": [
                {
                    "product_id": low_stock_product.json()["id"],
                    "quantity": 1,
                }
            ],
        },
    )
    assert order.status_code == 201

    response = client.get("/dashboard/stats")

    assert response.status_code == 200
    assert response.json() == {
        "total_products": 2,
        "total_customers": 1,
        "total_orders": 1,
        "pending_orders": 1,
        "low_stock_products": 1,
        "total_revenue": 50.0,
    }
