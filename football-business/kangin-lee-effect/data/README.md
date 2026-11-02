# Data

Raw data is not committed. YouTube's API terms restrict redistributing comment data, and every file can be regenerated from public sources with `notebooks/01_data_collection.ipynb`.

| File (created by the notebook) | Source | Grain |
| :---- | :---- | :---- |
| `raw/wikipedia_pageviews.csv` | Wikimedia Pageviews API, user agents only | entity × language × day |
| `raw/wikipedia_titles.json` | Wikipedia interlanguage links | entity |
| `raw/google_trends.csv` | Google Trends via `pytrends`, topic entities, rescaled to a Real Madrid anchor | entity × country × week/day |
| `raw/youtube_videos.csv` | YouTube Data API v3 | video |
| `raw/youtube_comments.csv` | YouTube Data API v3, top-level comments within 14 days of upload (no author data) | comment |
| `raw/youtube_comment_status.csv` | Download log (complete / truncated / disabled) | video |
| `processed/youtube_korean_share_per_video.csv` | Derived | video |
| `processed/youtube_korean_share_weekly.csv` | Derived | entity × upload week |

Collection window: Wikipedia and Trends from January 2022, YouTube from January 2026, all up to 1–2 November 2026.

The analysis outputs (no raw data) are in [`../results/`](../results/).
