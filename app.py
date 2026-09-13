from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data import load_data, period_slices
from src.diagnostics import decision_memo, dimension_deltas, ranked_actions
from src.metrics import compare_kpis, kpi_snapshot
from src.segments import calculate_rfm, cohort_retention, segment_summary


st.set_page_config(page_title="Commerce Operations Intelligence", page_icon="📈", layout="wide")

COLORS = {"navy": "#16324F", "blue": "#2B6CB0", "red": "#D64550", "green": "#238636", "gray": "#667085"}


@st.cache_data
def get_data():
    return load_data()


def fmt_metric(metric: str, value: float) -> str:
    if metric == "net_revenue":
        return f"¥{value:,.0f}"
    if metric in {"orders"}:
        return f"{value:,.0f}"
    if metric == "aov":
        return f"¥{value:,.0f}"
    return f"{value:.1%}"


def style_driver_table(frame: pd.DataFrame, dimension: str) -> pd.DataFrame:
    result = frame[[dimension, "previous_revenue", "current_revenue", "revenue_delta", "delta_pct", "share_of_decline"]].copy()
    result.columns = [dimension.title(), "Previous revenue", "Current revenue", "Revenue delta", "Delta %", "Share of decline"]
    return result


orders, sessions, customers = get_data()

st.title("Commerce Operations Intelligence")
st.caption("Diagnose KPI anomalies → locate business drivers → prioritize actions → design retention experiments")
st.info("Portfolio demo using reproducible simulated data. Driver signals support investigation; they do not establish causality.", icon="ℹ️")

with st.sidebar:
    st.header("Analysis settings")
    days = st.selectbox("Comparison window", [28, 56, 84], index=0, format_func=lambda value: f"Latest {value} days vs previous {value} days")
    channel_options = sorted(orders["channel"].unique())
    selected_channels = st.multiselect("Channels", channel_options, default=channel_options)
    st.divider()
    st.markdown("**Decision rule**")
    st.caption("Alert thresholds are metric-specific and documented in `docs/METRICS.md`.")
    st.markdown("**Owner**")
    st.caption("ZHANG JIN · Renmin University of China")

filtered_orders = orders[orders["channel"].isin(selected_channels)]
filtered_sessions = sessions[sessions["channel"].isin(selected_channels)]
current_orders, previous_orders, current_sessions, previous_sessions, bounds = period_slices(
    filtered_orders, filtered_sessions, days
)
current_kpis = kpi_snapshot(current_orders, current_sessions)
previous_kpis = kpi_snapshot(previous_orders, previous_sessions)
comparison = compare_kpis(current_kpis, previous_kpis)

channel_drivers = dimension_deltas(current_orders, previous_orders, "channel")
category_drivers = dimension_deltas(current_orders, previous_orders, "category")
region_drivers = dimension_deltas(current_orders, previous_orders, "region")
actions = ranked_actions(comparison, channel_drivers, category_drivers, region_drivers)

tab_diagnosis, tab_segments, tab_retention, tab_actions, tab_method = st.tabs(
    ["Executive diagnosis", "Customer segments", "Retention", "Action plan", "Method"]
)

with tab_diagnosis:
    st.subheader("Executive KPI diagnosis")
    st.caption(
        f"Current: {bounds['current_start'].date()} – {bounds['current_end'].date()} · "
        f"Previous: {bounds['previous_start'].date()} – {bounds['previous_end'].date()}"
    )

    display_metrics = ["net_revenue", "orders", "conversion_rate", "return_rate", "late_delivery_rate"]
    labels = {
        "net_revenue": "Net revenue",
        "orders": "Net orders",
        "conversion_rate": "Conversion rate",
        "return_rate": "Return rate",
        "late_delivery_rate": "Late delivery",
    }
    cols = st.columns(len(display_metrics))
    for col, metric in zip(cols, display_metrics):
        row = comparison.set_index("metric").loc[metric]
        col.metric(labels[metric], fmt_metric(metric, row["current"]), f"{row['delta_pct']:+.1%}")
        col.caption(f"Status: {row['status']}")

    st.divider()
    left, right = st.columns([1.35, 1])
    with left:
        trend = (
            filtered_orders.assign(valid_revenue=lambda x: x["net_revenue"])
            .groupby("order_date", as_index=False)["valid_revenue"]
            .sum()
        )
        trend = trend[trend["order_date"] >= bounds["previous_start"]]
        fig = px.line(trend, x="order_date", y="valid_revenue", title="Daily net revenue", markers=False)
        fig.add_vline(x=bounds["current_start"].timestamp() * 1000, line_dash="dash", line_color=COLORS["red"])
        fig.update_layout(yaxis_title="Net revenue (¥)", xaxis_title=None, hovermode="x unified")
        st.plotly_chart(fig, width="stretch")
    with right:
        status_counts = comparison.groupby("status").size().reindex(["Alert", "Watch", "Stable"], fill_value=0)
        fig = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            title="KPI status count",
            color=status_counts.index,
            color_discrete_map={"Alert": COLORS["red"], "Watch": "#E3A008", "Stable": COLORS["green"]},
        )
        fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Metrics")
        st.plotly_chart(fig, width="stretch")

    st.subheader("Where is the change coming from?")
    dimension = st.radio("Revenue decomposition", ["Channel", "Category", "Region"], horizontal=True)
    frame_map = {"Channel": (channel_drivers, "channel"), "Category": (category_drivers, "category"), "Region": (region_drivers, "region")}
    selected_frame, dimension_col = frame_map[dimension]
    fig = px.bar(
        selected_frame.sort_values("revenue_delta"),
        x="revenue_delta",
        y=dimension_col,
        orientation="h",
        color="revenue_delta",
        color_continuous_scale=[COLORS["red"], "#F2F4F7", COLORS["green"]],
        title=f"Net-revenue movement by {dimension.lower()}",
    )
    fig.update_layout(coloraxis_showscale=False, xaxis_title="Revenue delta (¥)", yaxis_title=None)
    st.plotly_chart(fig, width="stretch")
    st.dataframe(
        style_driver_table(selected_frame, dimension_col),
        width="stretch",
        hide_index=True,
        column_config={
            "Previous revenue": st.column_config.NumberColumn(format="¥%.0f"),
            "Current revenue": st.column_config.NumberColumn(format="¥%.0f"),
            "Revenue delta": st.column_config.NumberColumn(format="¥%.0f"),
            "Delta %": st.column_config.NumberColumn(format="%.1%%"),
            "Share of decline": st.column_config.ProgressColumn(format="%.1%%", min_value=0, max_value=1),
        },
    )

with tab_segments:
    st.subheader("Customer segmentation → retention treatment")
    st.caption("RFM is used as an explainable baseline. Each segment is connected to an objective, action, and success metric.")
    rfm = calculate_rfm(filtered_orders)
    summary = segment_summary(rfm)
    left, right = st.columns([1, 1.4])
    with left:
        fig = px.treemap(summary, path=["segment"], values="customers", color="revenue", title="Customer mix by RFM segment")
        st.plotly_chart(fig, width="stretch")
    with right:
        fig = px.scatter(
            summary,
            x="avg_recency_days",
            y="avg_frequency",
            size="revenue",
            color="segment",
            hover_name="segment",
            title="Segment behavior map",
        )
        fig.update_layout(xaxis_title="Average recency (days)", yaxis_title="Average order frequency", showlegend=False)
        st.plotly_chart(fig, width="stretch")
    segment_display = summary[["segment", "customers", "customer_share", "revenue", "objective", "recommended_action", "success_metric"]].copy()
    segment_display.columns = ["Segment", "Customers", "Share", "Revenue", "Objective", "Recommended action", "Success metric"]
    st.dataframe(
        segment_display,
        width="stretch",
        hide_index=True,
        column_config={
            "Share": st.column_config.NumberColumn(format="%.1%%"),
            "Revenue": st.column_config.NumberColumn(format="¥%.0f"),
        },
    )

with tab_retention:
    st.subheader("Monthly cohort retention")
    retention = cohort_retention(filtered_orders)
    max_months = min(8, retention.shape[1])
    display_retention = retention.iloc[:, :max_months]
    fig = go.Figure(
        data=go.Heatmap(
            z=display_retention.values,
            x=[f"M{int(col)}" for col in display_retention.columns],
            y=display_retention.index,
            colorscale="Blues",
            zmin=0,
            zmax=1,
            text=[[f"{value:.0%}" for value in row] for row in display_retention.values],
            texttemplate="%{text}",
            hovertemplate="Cohort %{y}<br>Month %{x}<br>Retention %{z:.1%}<extra></extra>",
        )
    )
    fig.update_layout(title="Share of cohort purchasing again", xaxis_title="Months since first purchase", yaxis_title="First-purchase cohort")
    st.plotly_chart(fig, width="stretch")
    st.markdown(
        "**How to use this:** identify the first month with the steepest drop, segment the affected cohort by acquisition channel and first category, then test one retention treatment with a holdout group."
    )

with tab_actions:
    st.subheader("Prioritized operating backlog")
    st.caption("Priority score = impact × confidence ÷ effort. Scores guide discussion; they do not replace owner judgment.")
    display_actions = actions.copy()
    display_actions.columns = [column.replace("_", " ").title() for column in display_actions.columns]
    st.dataframe(display_actions, width="stretch", hide_index=True)
    memo = decision_memo(bounds, comparison, actions)
    st.download_button(
        "Download decision memo",
        data=memo,
        file_name=f"decision-memo-{bounds['current_end'].date()}.md",
        mime="text/markdown",
        width="stretch",
    )

with tab_method:
    st.subheader("Method and limitations")
    st.markdown(
        """
        1. Compare the selected window with the immediately previous equal-length window.
        2. Apply visible, metric-specific business thresholds to label Stable / Watch / Alert.
        3. Decompose net-revenue movement by channel, category, and region.
        4. Convert signals into an action backlog with evidence, owner, and priority.
        5. Use RFM and cohort retention to define target groups and validation metrics.

        **Important limitations**

        - Injected anomalies make this a reproducible demonstration, not a real business diagnosis.
        - Period-over-period movement may reflect seasonality or mix effects.
        - Driver contribution is descriptive, not causal.
        - Retention actions are hypotheses that require experimentation.
        """
    )
    st.markdown("See `docs/METRICS.md`, `docs/PRD.md`, and `docs/TRANSFORMATION_LOG.md` in the repository for the full reasoning record.")

st.divider()
st.caption("Portfolio project by ZHANG JIN · AI-assisted development · Simulated data · Human verification required")
