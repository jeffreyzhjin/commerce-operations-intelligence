from __future__ import annotations

import math

import pandas as pd


LOWER_IS_BETTER = {"return_rate", "late_delivery_rate"}


def safe_divide(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def kpi_snapshot(orders: pd.DataFrame, sessions: pd.DataFrame) -> dict[str, float]:
    """Calculate the executive KPI set for one period."""
    valid_orders = orders.loc[~orders["returned"]]
    customer_order_counts = valid_orders.groupby("customer_id")["order_id"].nunique()
    return {
        "net_revenue": float(valid_orders["net_revenue"].sum()),
        "orders": float(valid_orders["order_id"].nunique()),
        "aov": safe_divide(valid_orders["net_revenue"].sum(), valid_orders["order_id"].nunique()),
        "conversion_rate": safe_divide(sessions["purchases"].sum(), sessions["sessions"].sum()),
        "repeat_customer_rate": safe_divide((customer_order_counts >= 2).sum(), len(customer_order_counts)),
        "return_rate": safe_divide(orders["returned"].sum(), orders["order_id"].nunique()),
        "late_delivery_rate": safe_divide(orders["delivered_late"].sum(), orders["order_id"].nunique()),
        "gross_margin": safe_divide(orders["gross_profit"].sum(), valid_orders["net_revenue"].sum()),
    }


def compare_kpis(current: dict[str, float], previous: dict[str, float]) -> pd.DataFrame:
    """Compare KPI values and label business-direction anomalies."""
    rows = []
    thresholds = {
        "net_revenue": 0.08,
        "orders": 0.08,
        "aov": 0.06,
        "conversion_rate": 0.10,
        "repeat_customer_rate": 0.10,
        "return_rate": 0.20,
        "late_delivery_rate": 0.20,
        "gross_margin": 0.08,
    }
    for metric, current_value in current.items():
        previous_value = previous.get(metric, 0.0)
        delta = safe_divide(current_value - previous_value, abs(previous_value))
        adverse_delta = -delta if metric not in LOWER_IS_BETTER else delta
        status = "Alert" if adverse_delta >= thresholds[metric] else "Watch" if adverse_delta >= thresholds[metric] / 2 else "Stable"
        if not math.isfinite(delta):
            delta = 0.0
        rows.append(
            {
                "metric": metric,
                "current": current_value,
                "previous": previous_value,
                "delta_pct": delta,
                "status": status,
                "threshold": thresholds[metric],
            }
        )
    return pd.DataFrame(rows)
