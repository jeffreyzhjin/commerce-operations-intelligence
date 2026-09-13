from __future__ import annotations

import pandas as pd


def dimension_deltas(current: pd.DataFrame, previous: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Decompose net-revenue movement by a selected business dimension."""
    current_group = current.groupby(dimension, as_index=False)["net_revenue"].sum().rename(columns={"net_revenue": "current_revenue"})
    previous_group = previous.groupby(dimension, as_index=False)["net_revenue"].sum().rename(columns={"net_revenue": "previous_revenue"})
    merged = previous_group.merge(current_group, on=dimension, how="outer").fillna(0)
    merged["revenue_delta"] = merged["current_revenue"] - merged["previous_revenue"]
    merged["delta_pct"] = merged.apply(
        lambda row: row["revenue_delta"] / abs(row["previous_revenue"]) if row["previous_revenue"] else 0.0,
        axis=1,
    )
    total_decline = abs(merged.loc[merged["revenue_delta"] < 0, "revenue_delta"].sum())
    merged["share_of_decline"] = merged["revenue_delta"].apply(
        lambda value: abs(value) / total_decline if value < 0 and total_decline else 0.0
    )
    return merged.sort_values("revenue_delta", ascending=True).reset_index(drop=True)


def ranked_actions(
    comparison: pd.DataFrame,
    channel_drivers: pd.DataFrame,
    category_drivers: pd.DataFrame,
    region_drivers: pd.DataFrame,
) -> pd.DataFrame:
    """Create an explainable execution backlog from detected signals."""
    actions: list[dict[str, object]] = []
    lookup = comparison.set_index("metric")

    def add(issue: str, evidence: str, action: str, impact: int, confidence: int, effort: int, owner: str) -> None:
        priority = round(impact * confidence / effort, 1)
        actions.append(
            {
                "issue": issue,
                "evidence": evidence,
                "recommended_action": action,
                "owner": owner,
                "impact": impact,
                "confidence": confidence,
                "effort": effort,
                "priority_score": priority,
            }
        )

    cvr = lookup.loc["conversion_rate"]
    if cvr["status"] in {"Alert", "Watch"}:
        worst = channel_drivers.iloc[0]
        add(
            "Conversion decline",
            f"Conversion changed {cvr['delta_pct']:+.1%}; {worst['channel']} contributed the largest revenue decline.",
            f"Audit {worst['channel']} traffic quality and landing-page mismatch; run a two-week creative × audience test.",
            5,
            4,
            2,
            "Growth + Product",
        )

    returns = lookup.loc["return_rate"]
    if returns["status"] in {"Alert", "Watch"}:
        worst = category_drivers.iloc[0]
        add(
            "Return-rate increase",
            f"Return rate changed {returns['delta_pct']:+.1%}; {worst['category']} has the weakest revenue movement.",
            f"Review {worst['category']} return reasons, product-page claims, and supplier quality; add a weekly guardrail.",
            4,
            4,
            3,
            "Category Operations",
        )

    late = lookup.loc["late_delivery_rate"]
    if late["status"] in {"Alert", "Watch"}:
        worst = region_drivers.iloc[0]
        add(
            "Delivery experience risk",
            f"Late-delivery rate changed {late['delta_pct']:+.1%}; {worst['region']} shows the weakest regional movement.",
            f"Split {worst['region']} by carrier and warehouse; trigger proactive delay messages for high-risk orders.",
            4,
            3,
            3,
            "Fulfilment Operations",
        )

    repeat = lookup.loc["repeat_customer_rate"]
    if repeat["status"] in {"Alert", "Watch"}:
        add(
            "Weak repeat purchase",
            f"Repeat-customer rate changed {repeat['delta_pct']:+.1%}.",
            "Launch segment-specific lifecycle messages and measure 30-day repeat purchase against a holdout group.",
            5,
            3,
            2,
            "CRM Operations",
        )

    if not actions:
        add(
            "No threshold breach",
            "Executive KPIs are within the current rule-based guardrails.",
            "Keep monitoring; validate whether thresholds should vary by season and channel.",
            2,
            4,
            1,
            "Business Operations",
        )

    return pd.DataFrame(actions).sort_values("priority_score", ascending=False).reset_index(drop=True)


def decision_memo(bounds: dict[str, pd.Timestamp], comparison: pd.DataFrame, actions: pd.DataFrame) -> str:
    alerts = comparison[comparison["status"] != "Stable"]
    alert_lines = "\n".join(
        f"- **{row.metric.replace('_', ' ').title()}**: {row.delta_pct:+.1%} ({row.status})"
        for row in alerts.itertuples()
    ) or "- No KPI crossed the current watch threshold."
    action_lines = "\n".join(
        f"{idx + 1}. **{row.issue}** — {row.recommended_action} Owner: {row.owner}. Priority: {row.priority_score}."
        for idx, row in enumerate(actions.itertuples())
    )
    return f"""# Commerce Operations Decision Memo

**Analysis window:** {bounds['current_start'].date()} to {bounds['current_end'].date()}  
**Comparison window:** {bounds['previous_start'].date()} to {bounds['previous_end'].date()}

## Signals

{alert_lines}

## Prioritized actions

{action_lines}

## Decision guardrails

- Driver contribution indicates association, not causation.
- Validate each action with a defined owner, primary KPI, guardrail metric, and review date.
- This memo is generated from simulated portfolio data.
"""
