# Data

Both files are derived from English Wikipedia season pages and are shared under the same licence as the source text ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)). Raw HTML pages are not committed; `notebooks/01_build_dataset.ipynb` downloads them again, and `source_revisions.csv` (created by the notebook) pins the exact revision of every page.

## `processed/club_seasons.csv`

One row per club and season: 1,782 rows, 141 clubs, LaLiga, Segunda, Premier League and Championship, 2005/06–2026/27 (Segunda from 2010/11: earlier pages have no kits table).

| Column | Meaning |
| :---- | :---- |
| `country`, `division`, `tier` | `ESP`/`ENG`, division slug, 1 or 2 |
| `season`, `season_label` | Start year (2021 = 2021/22) and label |
| `team` | Club name, harmonised between the kits table and the league table |
| `sponsor`, `sponsor_key` | Main front-of-shirt sponsor as listed, and its normalised key (joins to `sponsor_tags.csv`) |
| `multi_sponsor_flag` | The cell listed several sponsors or a mid-season change (first listed / home kit was kept) |
| `kit_maker` | Kit manufacturer |
| `pos`, `played`, `points`, `champion`, `promoted`, `relegated` | From the league table of the same page |
| `season_complete` | False for 2026/27 |
| `sponsor_raw`, `team_raw` | Original cell text, for auditing |

## `manual/sponsor_tags.csv`

One row per sponsor name (811), hand-labelled.

| Column | Meaning |
| :---- | :---- |
| `sponsor_key`, `sponsor` | Join key and name as it appears in the panel |
| `main_sponsor` | The single brand kept when the cell listed several |
| `brand` | Canonical brand (*Fly Emirates* → *Emirates*) |
| `sector` | One of: betting & gaming, crypto & trading apps, airline & travel, banking & insurance, real estate & construction, automotive, telecom & tech, food & drink, energy & utilities, retail & consumer goods, public body & tourism board, charity & club foundation, other, no sponsor |
| `brand_country` | ISO-3 country of the brand owner |
| `notes` | Reason for borderline tags (e.g. payment processors, possible gaming surrogates) |
| `club_seasons`, `clubs`, `countries`, `first_season`, `last_season` | Where the sponsor appears in the panel |
