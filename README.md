<table>
<tr>
<td width="300">
<img src="assets/profile.jpg" width="300" alt="Miguel Romero">
</td>
<td>

# Miguel Romero — Data Science & Analytics Portfolio

Data Scientist with a generalist, business-driven profile, working across retail, banking, marketing, and e-commerce. I combine a Master's in Data Science & AI with a previous career in linguistics and education — a background that shows up directly in how I communicate technical findings to non-technical stakeholders.

</td>
</tr>
</table>

**What I bring from my previous career:** clear communication, structuring complex information for different audiences, and adapting explanations to the listener — skills that transfer directly into translating model results into decisions a business stakeholder can act on.

**What differentiates my technical work:** most of the projects below don't stop at accuracy or AUC. Where relevant, I push further into business-driven evaluation — cost-sensitive thresholds, the actual error trade-offs a business would care about — rather than optimizing a metric in isolation.

## Stack

| Area | Tools |
| :---- | :---- |
| Languages | Python, SQL |
| ML / Modeling | scikit-learn, LightGBM, supervised ML, Deep Learning |
| Visualization / BI | Power BI, Tableau, Streamlit |
| Other | Pandas, Generative AI / agentic workflows (RAG, LangChain) |


## Projects

Projects live in two folders: **[`data-to-decisions/`](./data-to-decisions/)** — business cases where the analysis ends in a decision — and **[`football/`](./football/)**, a separate set of football analytics work.

### Data to Decisions — business projects

| Project | Stack | Description |
| :---- | :---- | :---- |
| [easyMoney Cross-Selling Campaign](./data-to-decisions/easymoney-cross-selling/) | Python, scikit-learn, Pandas, Power BI, Streamlit | End-to-end team project for a fintech: Power BI sales dashboard, propensity models for two products, K-Means segmentation into 8 customer groups, and a Monte Carlo profit simulation behind an interactive Streamlit simulator. Recommended campaign reaches 93% of the model's sales with half the contacts (~€13.7M estimated monthly profit, 90% interval €13.0–14.4M). Includes my [propensity deep dive](./data-to-decisions/easymoney-cross-selling/propensity-deep-dive/) on pension plans: temporal split, depth tuning, decile/lift analysis and a Random Forest benchmark. |
| [easyMoney Sales & Customer Dashboard](./data-to-decisions/easymoney-dashboard/) | Power BI, Python (pandas) | Five-page Power BI dashboard on 17 months of fintech sales (241K sales, 153K customers): KPIs, sales vs. margin by product, customer profile, sales map by province and product mix by customer type, with shared slicers. Shows that pension plans are under 10% of sales but drive most of the margin. |
| [Cost-Sensitive Malware Detection](./data-to-decisions/malware-detection/) | Python, scikit-learn, LightGBM, Pandas | Classification model on 500K devices with a leakage-free preprocessing pipeline; benchmarked 4 algorithms by AUC and optimized the decision threshold against a false-negative/false-positive cost matrix. |
| *Coming soon* | — | Project with less-clean data (scraping / API sourcing) |

### Football analytics

| Project | Stack | Description |
| :---- | :---- | :---- |
| [Data-Driven Scouting for RCD Mallorca](./football/Mallorca-scout/) | Python, Power BI | Player recommendation system for a club with a limited budget: open-data pipeline, custom scoring algorithm and interactive dashboard. |
| [Euro 2024 Midfield Comparison](./football/Hudl_Euro24_MF/) | Python, StatsBomb Open Data | Kroos vs. Rodri vs. Rice: event-data analysis and visual report on three midfield profiles. |

Each project folder contains its own README with full methodology, results, and business framing.

## Contact

- LinkedIn: [https://www.linkedin.com/in/miguel%C3%A1ngelromerotornero/](https://www.linkedin.com/in/miguel%C3%A1ngelromerotornero/)   
- Email: [migueromrto@gmail.com](mailto:migueromrto@gmail.com) 
