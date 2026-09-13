import pandas as pd

from src.metrics import compare_kpis, kpi_snapshot


def test_kpi_snapshot_uses_net_orders_and_safe_rates():
    orders = pd.DataFrame(
        {
            "order_id": ["1", "2", "3"],
            "customer_id": ["A", "A", "B"],
            "returned": [False, False, True],
            "net_revenue": [100.0, 200.0, 0.0],
            "gross_profit": [40.0, 80.0, -30.0],
            "delivered_late": [False, True, False],
        }
    )
    sessions = pd.DataFrame({"sessions": [100], "purchases": [3]})
    result = kpi_snapshot(orders, sessions)
    assert result["net_revenue"] == 300.0
    assert result["orders"] == 2.0
    assert result["aov"] == 150.0
    assert result["conversion_rate"] == 0.03
    assert result["repeat_customer_rate"] == 1.0
    assert result["return_rate"] == 1 / 3


def test_compare_kpis_respects_metric_direction():
    previous = {
        "net_revenue": 100.0,
        "orders": 100.0,
        "aov": 100.0,
        "conversion_rate": 0.10,
        "repeat_customer_rate": 0.10,
        "return_rate": 0.10,
        "late_delivery_rate": 0.10,
        "gross_margin": 0.40,
    }
    current = previous | {"net_revenue": 80.0, "return_rate": 0.14}
    result = compare_kpis(current, previous).set_index("metric")
    assert result.loc["net_revenue", "status"] == "Alert"
    assert result.loc["return_rate", "status"] == "Alert"
    assert result.loc["orders", "status"] == "Stable"
