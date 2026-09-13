import pandas as pd

from src.segments import calculate_rfm, cohort_retention


def sample_orders() -> pd.DataFrame:
    rows = []
    for customer_idx in range(1, 11):
        for order_idx in range(customer_idx):
            rows.append(
                {
                    "order_id": f"{customer_idx}-{order_idx}",
                    "customer_id": f"C{customer_idx}",
                    "order_date": pd.Timestamp("2025-01-01")
                    + pd.Timedelta(int(customer_idx * 10 + order_idx * 31), unit="D"),
                    "returned": False,
                    "net_revenue": 50.0 + customer_idx,
                }
            )
    return pd.DataFrame(rows)


def test_rfm_assigns_every_customer_to_one_segment():
    rfm = calculate_rfm(sample_orders(), as_of=pd.Timestamp("2026-01-01"))
    assert len(rfm) == 10
    assert rfm["segment"].notna().all()
    assert rfm[["r_score", "f_score", "m_score"]].min().min() >= 1
    assert rfm[["r_score", "f_score", "m_score"]].max().max() <= 5


def test_cohort_month_zero_is_full_retention():
    retention = cohort_retention(sample_orders())
    assert (retention[0] == 1.0).all()
