# Pension Plan Propensity Model — easyMoney (TFM Team Project)

Predicts which existing easyMoney customers are most likely to purchase
`pension_plan` — the highest-margin product in the portfolio (79% of total
margin) — in order to prioritize a limited-budget cross-sell campaign instead
of contacting the full customer base.

Built as part of a 4-person team's final Master's project (TFM), simulating a
real fintech business case. Full team repo:
[grupo-1-dscesp-0226](https://github.com/SandraMartinezg/grupo-1-dscesp-0226).

**My contribution:** manual depth tuning under a strict temporal split (to
avoid the leakage a standard cross-validation would introduce on monthly panel
data), feature importance analysis, decile/lift analysis translating model
output into expected campaign conversion, and a Random Forest benchmark to
validate the interpretability vs. performance trade-off.

## Problem framing

Out of ~5.9M customer-month records, which customers — among those who don't
yet have `pension_plan` — should be contacted first? The model outputs a
ranked probability score per customer, so the business can decide how deep
into the ranking to run a campaign based on available budget.

## Approach

| Step | Decision |
|---|---|
| Target | New acquisition (no product last month → has it this month) |
| Features | Demographic + behavioral variables, all lagged 1 month (no future leakage) |
| Split | Strict temporal train / test / validation — never random, to respect the monthly panel structure |
| Model | Decision Tree, depth selected via manual grid search on the temporal test set |
| Benchmark | Random Forest under identical conditions |
| Class imbalance | `class_weight='balanced'` (~0.7% positive rate) |

## Results

| Metric | Value |
|---|---|
| AUC (test) | 0.87 |
| Recall — positive class (test) | 0.87 |
| Conversion in top 10% of ranked customers | 3.64% vs. 0.66% random |
| Lift in top 10% | x5.5 |
| % of real buyers captured (top 10% contacted) | 55% |
| Conversion in top 5% | 4.65% — **x7.0** vs. random contact |

**Random Forest benchmark:** AUC 0.8744 vs. 0.8720 (Decision Tree) — a
marginal +0.0024 gain, but with ~750x more granular probability output
(71,682 vs. 96 distinct values). Kept the Decision Tree as the reference model
for its direct interpretability to business stakeholders; would recommend the
Random Forest if finer-grained ranking is needed in production.

## Key business insight

Feature importance shows customer **app activity** as by far the strongest
predictor (73%), well ahead of age (12%) or product holdings (6%). This
suggests that reactivating dormant customers may be as valuable to the
campaign's success as the targeting itself — an insight the technical metrics
alone wouldn't surface.

## Files

- [`propension_pension_plan_miguel.ipynb`](./propension_pension_plan_miguel.ipynb) — full technical notebook
- [`Informe_Propension_PensionPlan.pdf`](./Informe_Propension_PensionPlan.pdf) — executive summary, business-facing

## Stack

Python, pandas, scikit-learn (`DecisionTreeClassifier`, `RandomForestClassifier`), matplotlib, seaborn
