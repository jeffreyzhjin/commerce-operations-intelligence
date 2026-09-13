# Data Dictionary

All files in this folder are **synthetic** and reproducible with `python scripts/generate_data.py` (fixed seed `20260913`).

| File | Grain | Purpose |
|---|---|---|
| `orders.csv` | One row per order | Revenue, return, fulfilment, category, region, and customer analysis |
| `sessions_daily.csv` | One date × channel | Traffic funnel and conversion analysis |
| `customers.csv` | One row per customer | Acquisition and customer attributes |

Controlled signals in the final 28 days:

- Social traffic increases while its conversion rate declines.
- Beauty return probability increases.
- East-region late-delivery probability increases.

These signals exist solely to make the diagnostic workflow testable. They are not claimed as real findings.
