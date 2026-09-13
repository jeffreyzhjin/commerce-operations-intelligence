# Transformation Log

## Attribution

Technical reference: [ai-roman-novak/ecommerce-analytics-dashboard](https://github.com/ai-roman-novak/ecommerce-analytics-dashboard), MIT License, copyright Roman Novak (2025).

This project was developed by ZHANG JIN with AI-assisted coding. The goal was not to relabel an existing dashboard, but to reuse an appropriate open-source technical pattern and redesign the product around a different decision problem.

## Before / After

| Area | Open-source reference | This adaptation |
|---|---|---|
| User | General analytics viewer | Commerce operations manager / strategy analyst |
| Core question | What does store performance look like? | What is abnormal, why, and what should we do first? |
| Data model | Orders, products, customers, categories | Orders + acquisition funnel + fulfilment + customer lifecycle |
| Metrics | Descriptive revenue/product/customer metrics | Defined KPIs with direction, threshold, comparator, and guardrails |
| Analysis | Visual exploration | Equal-period anomaly flags and driver decomposition |
| Customer view | RFM description | RFM → segment objective → action → success metric |
| Output | Dashboard views | Ranked action backlog and downloadable decision memo |
| Validation | Portfolio screenshots | Fixed-seed anomaly injection plus unit tests |
| Documentation | Feature overview | PRD, metric dictionary, transformation record, limitations |

## Reused Ideas

- Python + Streamlit + Pandas + Plotly stack
- Modular separation of loading, analytics, and presentation
- RFM as an interpretable customer-analysis baseline
- Synthetic data for a safe, reproducible demonstration

## New Work

- New product definition and user stories
- New reproducible dataset and controlled anomaly scenarios
- New KPI definitions and directional alert logic
- New driver-decomposition and priority-scoring functions
- New RFM playbooks and cohort-retention analysis
- New decision memo export
- New automated tests and decision documentation

## AI Collaboration Disclosure

AI tools supported implementation, debugging, documentation, and test generation. ZHANG JIN owns the product framing, requirement choices, metric interpretation, validation decisions, and final presentation. This disclosure is intentional: the portfolio demonstrates the ability to direct AI-assisted development and evaluate its output.
