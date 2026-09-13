from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20260913
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def generate() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(SEED)
    dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    channels = ["Organic", "Paid Search", "Social", "Affiliate", "Email"]
    regions = ["North", "East", "South", "West", "Central"]
    categories = ["Electronics", "Home", "Beauty", "Sports", "Fashion"]
    customer_count = 4_000

    customers = pd.DataFrame(
        {
            "customer_id": [f"C{idx:05d}" for idx in range(1, customer_count + 1)],
            "signup_date": rng.choice(dates, customer_count),
            "acquisition_channel": rng.choice(channels, customer_count, p=[0.29, 0.25, 0.19, 0.12, 0.15]),
            "region": rng.choice(regions, customer_count, p=[0.20, 0.26, 0.19, 0.16, 0.19]),
        }
    ).sort_values("signup_date")

    base_sessions = {"Organic": 520, "Paid Search": 460, "Social": 410, "Affiliate": 240, "Email": 300}
    base_cvr = {"Organic": 0.040, "Paid Search": 0.034, "Social": 0.030, "Affiliate": 0.037, "Email": 0.051}
    session_rows: list[dict[str, object]] = []
    order_rows: list[dict[str, object]] = []
    order_id = 1
    end = dates.max()

    for date in dates:
        seasonality = 1 + 0.12 * np.sin(2 * np.pi * date.dayofyear / 365) + (0.18 if date.month in {11, 12} else 0)
        for channel in channels:
            sessions = int(max(80, rng.normal(base_sessions[channel] * seasonality, base_sessions[channel] * 0.08)))
            cvr = base_cvr[channel]
            # Controlled anomaly: low-quality Social traffic during the final 28 days.
            if channel == "Social" and date > end - pd.Timedelta(28, unit="D"):
                sessions = int(sessions * 1.25)
                cvr *= 0.56
            purchases = int(rng.binomial(sessions, cvr))
            add_to_cart = min(sessions, int(rng.binomial(sessions, min(cvr * 4.6, 0.35))))
            checkout = min(add_to_cart, int(rng.binomial(add_to_cart, 0.48)))
            session_rows.append(
                {
                    "date": date,
                    "channel": channel,
                    "sessions": sessions,
                    "add_to_cart": add_to_cart,
                    "checkout": checkout,
                    "purchases": purchases,
                }
            )

            for _ in range(purchases):
                # A clipped Zipf draw creates a realistic long tail of repeat buyers
                # without an expensive probability scan for every order.
                eligible_count = int(customers["signup_date"].searchsorted(date, side="right"))
                customer_idx = min(int(rng.zipf(1.24)) - 1, max(eligible_count - 1, 0))
                customer = customers.iloc[customer_idx]
                category = rng.choice(categories, p=[0.23, 0.22, 0.18, 0.17, 0.20])
                revenue_base = {"Electronics": 760, "Home": 420, "Beauty": 210, "Sports": 360, "Fashion": 290}[category]
                revenue = round(float(max(39, rng.lognormal(np.log(revenue_base), 0.42))), 2)
                cost_ratio = float(rng.uniform(0.50, 0.72))
                return_probability = {"Electronics": 0.06, "Home": 0.07, "Beauty": 0.08, "Sports": 0.07, "Fashion": 0.12}[category]
                if category == "Beauty" and date > end - pd.Timedelta(28, unit="D"):
                    return_probability = 0.24
                late_probability = 0.065
                if customer["region"] == "East" and date > end - pd.Timedelta(28, unit="D"):
                    late_probability = 0.19
                order_rows.append(
                    {
                        "order_id": f"O{order_id:07d}",
                        "customer_id": customer["customer_id"],
                        "order_date": date,
                        "channel": channel,
                        "region": customer["region"],
                        "category": category,
                        "revenue": revenue,
                        "cost": round(revenue * cost_ratio, 2),
                        "returned": bool(rng.random() < return_probability),
                        "delivered_late": bool(rng.random() < late_probability),
                    }
                )
                order_id += 1

    return pd.DataFrame(order_rows), pd.DataFrame(session_rows), customers


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    orders, sessions, customers = generate()
    orders.to_csv(DATA_DIR / "orders.csv", index=False)
    sessions.to_csv(DATA_DIR / "sessions_daily.csv", index=False)
    customers.to_csv(DATA_DIR / "customers.csv", index=False)
    print(f"Generated {len(orders):,} orders, {len(sessions):,} session rows, and {len(customers):,} customers.")


if __name__ == "__main__":
    main()
