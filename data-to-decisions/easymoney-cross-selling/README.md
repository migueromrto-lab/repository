# easyMoney — Cross-Selling Campaign: From Data to Decision

Collaborative data science project · Python · Power BI · Streamlit

easyMoney is a fintech that wants to shift its focus from acquiring new customers to selling more to the ones it already has (**cross-selling**). Using 17 months of customer and sales data (January 2018 – May 2019), our team answered four connected requests from management: what has happened, which product to offer to whom, who our customers are, and how much a campaign could earn.

**My contribution:** the propensity modelling for `pension_plan` — temporal split, depth tuning, decile/lift analysis and a Random Forest benchmark, documented in [`propensity-deep-dive/`](./propensity-deep-dive/) — and my own version of the Power BI dashboard, in [`easymoney-dashboard`](../easymoney-dashboard/).

> Notebooks, documentation and the simulator interface are in English; the campaign deck and the dashboard labels are in Spanish, as they were built for a Spanish-speaking business audience.

## The four tasks

| Task | Business question | Approach | Notebook |
|---|---|---|---|
| **1. Dashboard** | What have we sold, to whom, and where is the margin? | Cleaning and joining the 5 tables in Python; Power BI dashboard (sales and customers) — see [`easymoney-dashboard`](../easymoney-dashboard/) | `00_powerbi_limpieza` |
| **2. Propensity** | Which customers should be offered each product? | Customer-month panel with previous-month features; comparison of 4 models (logistic regression, decision tree, Random Forest and Gradient Boosting) for `pension_plan` and `em_acount`; scoring for June 2019 | `02_tarea2_propension` |
| **3. Segmentation** | Who are our customers? | Customers without products set apart + K-Means (k=7) on the rest → 8 named segments with a commercial profile | `03_tarea3_segmentacion` |
| **4. Economic impact** | How many customers should we contact and how much can we earn? | Propensity × segmentation; conversion measured on actual purchases; Monte Carlo simulation of profit; interactive Streamlit simulator | `04_tarea4_impacto_economico` + `app/` |

## Key results

- **The money is in pension plans:** they are 8% of sales but generate 79% of the margin. Each plan brings in about €6,000 on average; the easyMoney account, about €70.
- **The propensity model finds the buyers:** in the top 5% of customers by probability, actual May 2019 conversion is 13 times the average for `pension_plan` and 10 times for `em_acount`.
- **Segmentation tells us where to stop:** customers with their salary paid into the account buy pension plans about 20 times more often than average; three segments (74% of the customer base) hardly buy at all.
- **Proposed `pension_plan` campaign:** contact every customer in the salary and credit card segments and, in the remaining segments with potential, only the top 20% by model score. That is about **62,200 customers**, with a conversion rate of **3.7%** versus 0.66% at random and about **2,300 sales**: 93% of the sales the model alone would achieve, with half the contacts.
- **Estimated profit:** about €13.7M in one month (between €13.0M and €14.4M with 90% probability), under assumed cost-per-contact figures. We recommend validating it with a one-month pilot with a control group.

## Deep dive: `pension_plan` propensity

[`propensity-deep-dive/`](./propensity-deep-dive/) goes deeper into the highest-margin product: depth tuning under a strict temporal split, feature importance, decile/lift analysis and a Random Forest benchmark, plus an executive report in PDF. It is the detailed, single-model view of the problem; the campaign figures above come from the four-model comparison in `02_tarea2_propension`.

## Pipeline

```
                    ┌─► 00_powerbi_limpieza ──► df_powerbi.csv ──► Power BI (Task 1)
                    │
Raw CSV files ──────┤                        ┌─► 02_tarea2_propension ────┐
(data/raw)          │                        │                            │
                    └─► 01_base_comun ───────┼─► 03_tarea3_segmentacion ──┼─► 04_tarea4_impacto_economico ──► data/app ──► app/simulador.py
                                             │                            │
                                             └─────── (clean sales) ──────┘
```

All cleaning and imputation for the modelling part is done **only once**, in `01_base_comun` (common base). Each task then builds its own features from that shared base. The Power BI dashboard has its own cleaning branch (`00`), independent from the rest.

| File | Created by | Used by |
|---|---|---|
| `data/processed/df_powerbi.csv` | 00 | Power BI |
| `data/processed/df_panel_limpio.parquet` | 01 | 02, 03 |
| `data/processed/df_sales_limpio.parquet` | 01 | 04 |
| `data/processed/scoring_{producto}.csv` | 02 | 04 |
| `data/processed/validacion_{producto}.csv` | 02 | 04 |
| `data/processed/comparacion_modelos_{producto}.csv`, `lift_{producto}.csv` | 02 | Reference |
| `data/processed/clientes_grupos_abril.csv` | 03 | 04 (measure May conversion) |
| `data/processed/clientes_grupos.csv` | 03 | 04 (June campaign list) |
| `data/app/*.csv` | 04 | `app/simulador.py` |

`{producto}` (product) is `pension_plan` or `em_acount`. File names are kept in Spanish because the code reads and writes them.

## Repository structure

```
easymoney-cross-selling/
├── app/
│   ├── simulador.py        Campaign simulator (Streamlit)
│   ├── requirements.txt
│   ├── README.md
│   └── assets/logo.png
├── data/
│   ├── raw/                Original CSV files + data dictionary (not included)
│   ├── processed/          Notebook outputs (regenerated when they run)
│   └── app/                Lightweight data read by the simulator (included)
├── propensity-deep-dive/   My pension_plan propensity work: notebook + executive report
├── notebooks/
│   ├── 00_powerbi_limpieza.ipynb          Power BI data cleaning
│   ├── 01_base_comun.ipynb                Common base (cleaning + imputation)
│   ├── 02_tarea2_propension.ipynb         Task 2 · Propensity models
│   ├── 03_tarea3_segmentacion.ipynb       Task 3 · Segmentation
│   └── 04_tarea4_impacto_economico.ipynb  Task 4 · Economic impact
├── powerbi/
│   └── Dashboard_EasyMoney.pbix
├── Presentación/
│   └── easyMoney — Propuesta de campaña.pptx   Campaign proposal deck (Spanish)
└── README.md
```

## Data

The original CSV files are not included because of their size (about 950 MB). To reproduce the project, place these files in `data/raw/`:

- `sales.csv`
- `customer_sociodemographics.csv`
- `customer_commercial_activity.csv`
- `customer_products.csv`
- `product_description.csv`
- `diccionario_tablas.xlsx` (data dictionary)

The files in `data/app/` are included, so the simulator works without running the notebooks first.

## How to reproduce it

**Environment.** Python 3.9 with `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn` and `pyarrow`.

**Notebooks.** Run them in order: `01` → `02` → `03` → `04`. `02` and `03` depend only on `01` and can run in either order; `04` needs both. `00` is independent and only needed for the dashboard. Paths are relative to the `notebooks/` folder, so open them from there.

**Power BI.** `powerbi/Dashboard_EasyMoney.pbix` reads `data/processed/df_powerbi.csv` (`;` separator, `,` decimal). When opening it on another machine, update the data source path.

**Simulator.** From the repository root:

```bash
pip install -r app/requirements.txt
streamlit run app/simulador.py
```

More details in [`app/README.md`](app/README.md).

## A note on variable names

`em_acount` (missing the second "c") is the official spelling in the data dictionary and is kept as-is throughout the project.
