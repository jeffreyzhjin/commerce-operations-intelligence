# Commerce Operations Intelligence

> A decision-oriented Streamlit dashboard for diagnosing commerce KPI anomalies and translating customer segments into retention actions.

🚀 **[Try the Live Demo](https://zhang-jin-commerce-operations.streamlit.app/)**

**Portfolio project by ZHANG JIN · Renmin University of China**

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41%2B-FF4B4B)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Why This Product

Many dashboards answer “what happened” but stop before “why” and “what should we do next.” This MVP is designed for an e-commerce operations manager who needs to:

1. detect abnormal KPI movements;
2. locate likely drivers by channel, category, and region;
3. prioritize actions by expected business impact;
4. design differentiated retention actions for customer segments.

The sample dataset intentionally contains several controlled anomalies, so the diagnostic workflow can be tested end to end.

> **Data notice:** all records are reproducible synthetic data created for portfolio demonstration. They do not represent a real company, customer, or business result.

## Product Workflow

```mermaid
flowchart LR
    A[Monitor KPIs] --> B[Flag anomalies]
    B --> C[Trace drivers]
    C --> D[Prioritize actions]
    D --> E[Track retention]
```

## MVP Capabilities

- Executive KPI comparison for the current and previous equal-length periods
- Rule-based anomaly flags with visible definitions
- Revenue-driver decomposition by channel, category, and region
- RFM customer segmentation with segment-specific retention playbooks
- Monthly cohort retention matrix
- Action backlog ranked by impact, confidence, and effort
- Downloadable Markdown decision memo
- Reproducible synthetic-data generator and automated unit tests

## Quick Start

```bash
git clone https://github.com/jeffreyzhjin/commerce-operations-intelligence.git
cd commerce-operations-intelligence
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python scripts/generate_data.py
streamlit run app.py
```

## Project Structure

```text
commerce-operations-intelligence/
├── app.py                    # Streamlit decision dashboard
├── data/                     # Reproducible simulated data
├── docs/
│   ├── METRICS.md            # Metric dictionary and guardrails
│   ├── PRD.md                # Product requirements document
│   └── TRANSFORMATION_LOG.md # What changed from the open-source base
├── scripts/generate_data.py  # Fixed-seed data generation
├── src/
│   ├── data.py               # Loading and period selection
│   ├── diagnostics.py        # Driver and action logic
│   ├── metrics.py            # KPI calculation and comparison
│   └── segments.py           # RFM and cohort retention
└── tests/                    # Unit tests for business logic
```

## Product Decisions

| Decision | Rationale |
|---|---|
| Equal-length period comparison | Makes KPI movement interpretable without mixing window sizes |
| Rule-based anomaly flags | Keeps the MVP explainable and auditable for operators |
| RFM before machine learning | Provides a transparent baseline that can be challenged and improved |
| Impact–confidence–effort priority | Forces the dashboard to recommend an execution order, not just observations |
| Synthetic data with injected anomalies | Makes the complete diagnostic loop reproducible without exposing company data |

## Limitations and Next Experiments

- Current anomaly thresholds are business rules, not statistically learned baselines.
- Driver tables show contribution and correlation, not causal proof.
- Retention actions are hypotheses and require controlled experiments.
- Next version: seasonality-aware alerts, experiment tracking, and LLM-assisted narrative generation with source-bound evidence.

## Open-source Adaptation Statement

This project uses the MIT-licensed repository [ai-roman-novak/ecommerce-analytics-dashboard](https://github.com/ai-roman-novak/ecommerce-analytics-dashboard) as a technical reference for a modular Streamlit/Pandas/Plotly analytics application.

The business problem, product scope, metric system, simulated data model, anomaly logic, diagnostic workflow, retention playbooks, decision memo, documentation, and tests were redesigned for this portfolio project by **ZHANG JIN**, using AI-assisted development. See [Transformation Log](docs/TRANSFORMATION_LOG.md) for a concrete before/after comparison. The original copyright notice is retained in [LICENSE](LICENSE).

## 中文说明

这是一个面向电商业务/产品运营的经营分析项目。它重点展示的不是“会画图”，而是把数据转化为经营动作：监控核心指标、识别异常、拆解渠道/品类/区域驱动因素、进行用户分层，并形成留存策略和执行优先级。

## License

MIT. See [LICENSE](LICENSE).
