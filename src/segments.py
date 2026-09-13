from __future__ import annotations

import numpy as np
import pandas as pd


PLAYBOOKS = {
    "Champions": ("Protect", "Early access + referral program", "Repeat purchase rate"),
    "Loyal": ("Grow", "Cross-category recommendation", "Orders per customer"),
    "Promising": ("Activate", "Second-order incentive within 14 days", "Second-order conversion"),
    "Needs Attention": ("Nurture", "Behavior-based content and reminders", "30-day active rate"),
    "At Risk": ("Recover", "Win-back journey based on last category", "Reactivation rate"),
    "Hibernating": ("Limit cost", "Low-cost re-permission campaign", "Incremental margin"),
}


def _score(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    ranked = series.rank(method="first")
    score = pd.qcut(ranked, 5, labels=[1, 2, 3, 4, 5]).astype(int)
    return score if higher_is_better else 6 - score


def calculate_rfm(orders: pd.DataFrame, as_of: pd.Timestamp | None = None) -> pd.DataFrame:
    """Calculate transparent RFM segments from non-returned orders."""
    valid = orders.loc[~orders["returned"]].copy()
    reference = pd.Timestamp(as_of) if as_of is not None else pd.Timestamp(valid["order_date"].max())
    reference += pd.Timedelta(1, unit="D")
    rfm = valid.groupby("customer_id").agg(
        last_order=("order_date", "max"),
        frequency=("order_id", "nunique"),
        monetary=("net_revenue", "sum"),
    )
    rfm["recency_days"] = (reference - rfm["last_order"]).dt.days
    rfm["r_score"] = _score(rfm["recency_days"], higher_is_better=False)
    rfm["f_score"] = _score(rfm["frequency"], higher_is_better=True)
    rfm["m_score"] = _score(rfm["monetary"], higher_is_better=True)

    conditions = [
        (rfm["r_score"] >= 4) & (rfm["f_score"] >= 4),
        rfm["f_score"] >= 4,
        (rfm["r_score"] >= 4) & (rfm["f_score"] <= 3),
        (rfm["r_score"] <= 2) & (rfm["f_score"] >= 3),
        (rfm["r_score"] <= 2) & (rfm["f_score"] <= 2),
    ]
    labels = ["Champions", "Loyal", "Promising", "At Risk", "Hibernating"]
    rfm["segment"] = np.select(conditions, labels, default="Needs Attention")
    return rfm.reset_index()


def segment_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    summary = rfm.groupby("segment", as_index=False).agg(
        customers=("customer_id", "nunique"),
        revenue=("monetary", "sum"),
        avg_frequency=("frequency", "mean"),
        avg_recency_days=("recency_days", "mean"),
    )
    summary["customer_share"] = summary["customers"] / summary["customers"].sum()
    summary["objective"] = summary["segment"].map(lambda value: PLAYBOOKS[value][0])
    summary["recommended_action"] = summary["segment"].map(lambda value: PLAYBOOKS[value][1])
    summary["success_metric"] = summary["segment"].map(lambda value: PLAYBOOKS[value][2])
    return summary.sort_values("revenue", ascending=False).reset_index(drop=True)


def cohort_retention(orders: pd.DataFrame) -> pd.DataFrame:
    """Return a customer cohort retention matrix indexed by first-order month."""
    valid = orders.loc[~orders["returned"], ["customer_id", "order_date"]].drop_duplicates()
    valid["order_month"] = valid["order_date"].dt.to_period("M")
    first_month = valid.groupby("customer_id")["order_month"].min().rename("cohort_month")
    valid = valid.join(first_month, on="customer_id")
    valid["cohort_index"] = (
        (valid["order_month"].dt.year - valid["cohort_month"].dt.year) * 12
        + valid["order_month"].dt.month
        - valid["cohort_month"].dt.month
    )
    cohort = valid.groupby(["cohort_month", "cohort_index"])["customer_id"].nunique().unstack(fill_value=0)
    sizes = cohort.iloc[:, 0]
    retention = cohort.divide(sizes, axis=0)
    retention.index = retention.index.astype(str)
    return retention
