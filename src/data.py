from __future__ import annotations

from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_data(data_dir: Path | str = DATA_DIR) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load orders, daily sessions, and customers from CSV files."""
    base = Path(data_dir)
    orders = pd.read_csv(base / "orders.csv", parse_dates=["order_date"])
    sessions = pd.read_csv(base / "sessions_daily.csv", parse_dates=["date"])
    customers = pd.read_csv(base / "customers.csv", parse_dates=["signup_date"])

    orders["returned"] = orders["returned"].astype(bool)
    orders["delivered_late"] = orders["delivered_late"].astype(bool)
    orders["net_revenue"] = orders["revenue"].where(~orders["returned"], 0.0)
    orders["gross_profit"] = (orders["net_revenue"] - orders["cost"]).round(2)
    return orders, sessions, customers


def period_slices(
    orders: pd.DataFrame,
    sessions: pd.DataFrame,
    days: int,
    end_date: pd.Timestamp | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, pd.Timestamp]]:
    """Return current and previous equal-length analysis windows."""
    end = pd.Timestamp(end_date or orders["order_date"].max()).normalize()
    current_start = end - pd.Timedelta(days=days - 1)
    previous_end = current_start - pd.Timedelta(days=1)
    previous_start = previous_end - pd.Timedelta(days=days - 1)

    current_orders = orders[orders["order_date"].between(current_start, end)].copy()
    previous_orders = orders[orders["order_date"].between(previous_start, previous_end)].copy()
    current_sessions = sessions[sessions["date"].between(current_start, end)].copy()
    previous_sessions = sessions[sessions["date"].between(previous_start, previous_end)].copy()
    bounds = {
        "current_start": current_start,
        "current_end": end,
        "previous_start": previous_start,
        "previous_end": previous_end,
    }
    return current_orders, previous_orders, current_sessions, previous_sessions, bounds
