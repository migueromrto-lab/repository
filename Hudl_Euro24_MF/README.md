# Euro 2024 Midfield Comparison: Kroos vs. Rodri vs. Rice

**Data analysis & visualization project — StatsBomb open data**

<p align="center">
  <img src="assets/progr.png" width="600" alt="Progressive passes: Kroos vs Rodri">
</p>

## 1. The Question

Euro 2024 was decided in the midfield. Three players, three different profiles at the same position — Toni Kroos (creative), Rodri (holding midfielder, Player of the Tournament), and Declan Rice (box-to-box) — raised an obvious question: who actually had the bigger impact, and how do their styles differ once you look past the eye test?

## 2. Data Source

- **StatsBomb Euro 2024 open dataset**, accessed via the `statsbombpy` API (competition_id=55, season_id=282).
- Full event-level, lineup, and 360° freeze-frame data pulled for every match of the tournament.

## 3. Data Pipeline

1. **Extraction** — looped through every Euro 2024 match, pulling events, lineups, and 360 frames per match_id, with error handling per match to avoid a single failed request breaking the full run; concatenated into three master DataFrames (events, lineups, frames360).
2. **Schema normalization** — StatsBomb's event data mixes flat and nested column names depending on event type (e.g. `type` vs `type.name`); built a `pick_col()` helper to resolve the right column robustly instead of hardcoding assumptions.
3. **Player-level aggregation** — computed minutes played per player per match (from max event minute), total minutes, matches played, and primary team/position (by mode across events), as the base table every other metric is joined onto.
4. **Per-90 normalization** — all volume metrics (passes, shots, defensive actions, etc.) converted to per-90 rates with division-by-zero protection, to make cross-player comparison fair regardless of minutes played.

## 4. Analysis & Visualizations

- **Percentile radar** — the three players benchmarked against all tournament midfielders across passing, progression, defensive, and offensive metrics, to visualize style differences at a glance rather than relying on raw totals.
- **Progressive pass maps** — arrow maps of each player's progressive passes across the pitch, completed vs. incomplete.
- **Line-breaking pass detection** — a custom method using 360° freeze-frame data: for each pass, the furthest-forward opponent position at that moment is taken as a "defensive line" proxy, and a pass is flagged as line-breaking if it starts behind that line and ends beyond it. This goes beyond standard event data and required combining events with spatial (360) data.
- **Shot maps** — shot locations sized by xG, comparing shot selection and quality across the three players.
- **Defensive action heatmaps** — smoothed (Gaussian-filtered) heatmaps of pressures, tackles, interceptions, blocks, and clearances, normalized on a shared color scale for direct visual comparison.

## 5. Key Findings

- **Kroos** was the tournament's progression reference point — highest volume of progressive and line-breaking passes, with a marked tendency to switch play from his weaker foot down the right.
- **Rodri** combined the most complete defensive box coverage (91st+ percentile in clearances/blocks) with elite pass accuracy sustaining Spain's possession-based control — the most balanced profile of the three.
- **Rice** stood out offensively for a defensive midfielder: highest xG (0.4) and box touches (2.9/90) of the three, trading some build-up involvement for penalty-box presence in England's system.
- The comparison shows why raw stats alone are insufficient: each player's numbers only make sense in the context of their team's tactical framework.

## 6. Tech Stack

`Python` · `pandas` / `numpy` · `matplotlib` · `statsbombpy` (StatsBomb API) · `mplsoccer` (pitch visualizations) · `scipy` (heatmap smoothing)

## 7. Repository Structure

```
.
├── README.md
├── notebooks/
│   └── obtaining_data_and_visualizations.ipynb
├── report/
│   └── euro_2024_midfield_comparison.pdf
└── assets/
    └── radar_comparison.png
```

## 8. Notes

This was a timed technical exercise, not a production pipeline — some design choices (e.g. player-name matching via full names rather than IDs) reflect the scope and time constraints of the assessment rather than how I'd approach the same problem with more time or in a business context outside sports.
