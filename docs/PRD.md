# Product Requirements Document

## 1. Product Summary

| Item | Detail |
|---|---|
| Product | Commerce Operations Intelligence |
| Owner | ZHANG JIN |
| Version | MVP 1.0 |
| Primary user | E-commerce business / product operations manager |
| Core job | Diagnose operating anomalies and prioritize corrective actions |
| Secondary job | Segment users and design measurable retention actions |

## 2. Problem

Operations teams often review traffic, revenue, fulfilment, and customer reports separately. When a headline KPI moves, they spend time reconciling definitions and manually searching for drivers. Many dashboards visualize the movement but do not create an actionable, owned backlog.

## 3. Product Goal

Reduce the path from KPI signal to testable action by connecting four layers:

1. **Signal:** Which KPI moved outside a visible guardrail?
2. **Driver:** Which channel, category, or region explains the largest share?
3. **Decision:** What action should be prioritized, by whom, and why?
4. **Validation:** Which metric and customer group should validate the action?

## 4. MVP Scope

### In scope

- Equal-period KPI monitoring
- Rule-based anomaly status
- Channel/category/region revenue decomposition
- RFM segmentation
- Monthly cohort retention
- Explainable action ranking
- Downloadable decision memo

### Out of scope

- Real-time data ingestion
- Causal inference
- Automated campaign execution
- Personally identifiable information
- Production-grade alerting and access control

## 5. Key User Stories

- As an operations manager, I want to compare the latest 28/56/84 days against the prior period so I can spot abnormal movement.
- As an analyst, I want to see the dimensions contributing most to a decline so I can form investigation hypotheses.
- As a CRM operator, I want transparent customer segments and suggested treatments so I can design retention experiments.
- As a team lead, I want a ranked action backlog and downloadable memo so I can assign owners and review outcomes.

## 6. Acceptance Criteria

- The app starts from a clean environment using the documented commands.
- The latest 28-day window reveals the injected conversion, return, and delivery risks.
- Every KPI has a documented definition and direction.
- Every recommended action contains evidence, owner, and priority score.
- Segment actions include a success metric rather than only descriptive labels.
- Unit tests cover KPI directionality and core RFM/cohort logic.

## 7. Success Metrics for a Real Pilot

| Layer | Metric | Target hypothesis |
|---|---|---|
| Efficiency | Time from alert to first diagnosis | Reduce by 40% |
| Adoption | Weekly active operations users | ≥70% of target team |
| Decision quality | Actions with owner + metric + review date | ≥90% |
| Business learning | Completed controlled experiments per month | ≥3 |

Targets are hypotheses for a future pilot, not achieved results.
