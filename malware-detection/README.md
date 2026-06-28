# Malware Detection from Device Telemetry

Binary classification project on the Microsoft Malware Prediction dataset: predicting whether a device has detected malware based on \~80 hardware, OS, and security-configuration features.

## Business framing

In a real security operations context, **not all classification errors cost the same**. A false negative (an infected device classified as clean) is far more expensive than a false positive (a clean device flagged for review) — it means an active infection going unaddressed. This project goes beyond standard accuracy/AUC reporting and includes a **cost-based threshold optimization** step: assigning relative costs to false negatives vs. false positives and finding the classification threshold that minimizes total expected business cost, rather than defaulting to the standard 0.5 cutoff.

This cost-sensitive evaluation step is the main differentiator of this project versus a typical classification exercise.

## Dataset note

The target variable (`HasDetections`) is artificially balanced 50/50 by the Kaggle competition design — this does not reflect a real-world infection rate. This caps the achievable AUC regardless of the algorithm used, and is called out explicitly in the notebook's conclusions.

## Approach

1. **EDA** — identified sentinel values disguised as real data (e.g. a uint32-max placeholder for "missing"), MNAR nulls that carry signal (e.g. missing default browser ID), and a counter-intuitive relationship between active protection and the target (the label measures *detection*, not *infection*, so more protection means more detection capability).  
2. **Leakage-safe preprocessing pipeline** — all data-dependent steps (frequency encoding, categorical grouping by frequency threshold, outlier capping, low-variance filtering) are fit on the training set only and applied to test, instead of being computed on the full dataset before the split.  
3. **Model comparison** — Decision Tree, Random Forest, Gradient Boosting, and LightGBM, selected by AUC rather than accuracy alone (accuracy is uninformative on a balanced target). LightGBM was added after benchmarking showed Gradient Boosting's exact-split search to be impractically slow at this row count (\~30x slower for comparable AUC); LightGBM's histogram-based splitting gave the same modeling quality in a fraction of the training time.  
4. **Hyperparameter tuning** via `RandomizedSearchCV` on a reduced training sample (chosen over an exhaustive grid search for the same speed reason above) — the final model is still refit on the full training set with the best parameters found.  
5. **Final model: LightGBM**, selected for its combination of competitive AUC and practical training time on \~400K rows.  
6. **Cost-based threshold optimization** — sweeping classification thresholds against an explicit cost matrix (false negative cost \> false positive cost) to find the threshold that minimizes total expected cost, compared against the default 0.5 threshold. The cost reduction percentage is computed directly in the notebook rather than estimated by hand.

## Results

| Metric | Value |
| :---- | :---- |
| Final model | LightGBM |
| Test AUC | 0.7049 |
| Default threshold (0.5) — total cost | 107186 |
| Optimized threshold — total cost | 49446 |
| Cost reduction | 53.9% |

## Key takeaway

The most predictive features relate to **security configuration** (SmartScreen status, antivirus product state), not hardware profile — consistent with the dataset measuring detection capability rather than actual infection.

## Next steps

- Validate the false-negative/false-positive cost assumptions with a real security/business stakeholder (the ratio used here is illustrative).  
- Re-run on the dataset without artificial target balancing to get a more realistic performance ceiling.  
- Further feature engineering on remaining high-cardinality `_Identifier` columns.

## Stack

Python, pandas, scikit-learn (DecisionTree, RandomForest, GradientBoosting, RandomizedSearchCV), LightGBM, matplotlib, seaborn.  
