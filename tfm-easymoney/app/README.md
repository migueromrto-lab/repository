# easyMoney · Campaign Simulator (Task 4)

Streamlit app that combines the propensity model (Task 2) and the segmentation (Task 3) so the business team can simulate a cross-selling campaign and instantly see its economic outcome, with a confidence interval.

## Run it

From the repository root, with Python 3.9:

```bash
pip install -r app/requirements.txt
streamlit run app/simulador.py
```

## What you can decide (sidebar)

- **Product:** `pension_plan` or `em_acount`.
- **Channel / cost per contact:** from €0.10 (push notification or email) to €60, plus a fixed campaign cost.
- **What to do with each Task 3 segment:** contact *everyone*, only the *model's top X%*, or *exclude* it. The default proposal comes from each segment's actual conversion in validation, using the same rule as notebook 04: *everyone* if it converts at least twice the average (with at least 30 purchases), *exclude* if it converts less than half the average, and *model's top X%* otherwise.
- **Model cutoff:** in the *model's top X%* segments, the percentage of best-scored customers to contact (20% by default).
- **Number of Monte Carlo simulations.**

With the default values, the app reproduces the campaign recommended in notebook 04.

## What it shows

- **KPI cards:** customers contacted, expected sales and conversion, campaign cost, and net profit with its 90% interval.
- **Where to stop?** profit depending on how many customers from the remaining segments are added (from 0% to 50% of the model, in steps of 5). The green dot is the current configuration.
- **Who we contact:** contacts, conversion and expected sales by segment.
- **Confidence interval:** distribution of profit across simulations, with conservative (p5), base (p50) and optimistic (p95) scenarios.
- **Assumptions and limitations**, in an expandable section.

## How it calculates

The logic is the same as in notebook 04:

1. The selection rule is **measured** on validation data (probability with data up to April, April segment and actual May 2019 purchase) to get the conversion rate.
2. The same rule is **applied** to the scoring data (June customers with their May segment) to know how many customers are contacted.
3. Profit = contacts × conversion × average margin − cost.
4. **Monte Carlo:** in each simulation, conversion is sampled from a Beta distribution fitted to validation purchases, sales from a Binomial, and margin from the product's actual sales. A fixed seed makes it reproducible.

Segment names are not hard-coded: they are read from the data (which keeps the original Spanish names) and shown in English in the interface; any new segment name is displayed as it appears in the data.

## Data it needs

The CSV files in `data/app/`, created by the last section of `notebooks/04_tarea4_impacto_economico.ipynb`:

| File | Contents |
|---|---|
| `validacion_grupo_{producto}.csv` | Probability, actual May purchase and April segment for each customer |
| `scoring_grupo_{producto}.csv` | June probability and May segment for each eligible customer |
| `margenes_{producto}.csv` | Actual margin of each sale of the product |

If a model or the segmentation is retrained, simply re-run notebook 04; the app code does not change.

## Limitations

- Conversion is measured over a single month (May 2019) and assumed to hold for the campaign.
- Results cover one month and are not annualised.
- These are sales the model identifies, not necessarily attributable to the campaign: measuring the real effect requires a pilot with a control group.
- Costs are business assumptions, which is why they can be changed in the sidebar.
