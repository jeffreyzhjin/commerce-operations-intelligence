# Metric Dictionary

| Metric | Definition | Desired direction | Watch / alert rule |
|---|---|---|---|
| Net revenue | Revenue from non-returned orders | Higher | -4% / -8% |
| Net orders | Count of non-returned orders | Higher | -4% / -8% |
| AOV | Net revenue ÷ net orders | Higher | -3% / -6% |
| Conversion rate | Purchases ÷ sessions | Higher | -5% / -10% |
| Repeat-customer rate | Customers with ≥2 valid orders ÷ purchasing customers in the window | Higher | -5% / -10% |
| Return rate | Returned orders ÷ all orders | Lower | +10% / +20% |
| Late-delivery rate | Late orders ÷ all orders | Lower | +10% / +20% |
| Gross margin | (Net revenue − cost) ÷ net revenue | Higher | -4% / -8% |

## Interpretation Rules

- The dashboard compares the selected period with the immediately preceding equal-length period.
- Thresholds are explainable MVP rules, not statistical confidence intervals.
- A dimension's “share of decline” divides its negative revenue change by the sum of all negative dimension changes.
- RFM scores use within-dataset quintiles. Segment definitions therefore move with the observed customer base.
- Cohort retention measures the share of customers in a first-purchase cohort who purchase again in month *n*.

## Guardrails

- Revenue-driver tables support prioritization but do not prove causality.
- Return and delivery investigations should use reason/carrier-level data before a real decision.
- Retention playbooks must be evaluated with a holdout or controlled experiment.
