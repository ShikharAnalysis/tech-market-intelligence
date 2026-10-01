# MarketLens — Technology Market Opportunity Intelligence

**Which federal technology service segments should a mid-sized IT consulting firm investigate first?**

An independent data analytics and consulting portfolio project prepared for **Shikhar Mishra**. It converts a real USAspending snapshot into a transparent research shortlist, using Python, SQL, an interactive dashboard and a decision memo.

> This is a portfolio case study, not work commissioned by Gartner or a government agency. Code and documentation were developed with AI assistance. The repository owner should validate, understand and adapt the analysis before representing it in an interview.

![MarketLens opportunity ranking](reports/ranking-preview.svg)

## Open it immediately

Download this repository and **double-click `index.html`**. The dashboard is self-contained and works offline. No account, API key, Python package installation or server is required to view it.

Change the decision weights, filter agencies, inspect chart tooltips and download the current ranking. Read [the decision memo](reports/DECISION_MEMO.md) for the recommendation and its limits.

## What makes this an analytical project?

- **Real source data:** 36 complete paginated API queries across 3 fiscal years, 4 agencies and 3 service categories.
- **Reproducible pipeline:** raw responses and requests, SHA-256 manifest, integer-cent monetary storage, CSVs and SQLite database.
- **Actual SQL:** grouping, conditional aggregation, joins, window functions and ranked supplier shares; executed by the pipeline.
- **Business judgment:** relative opportunity score and four sensitivity scenarios; eligibility and delivery fit are explicit follow-up gates.
- **Quality checks:** pagination, unique grain, source hashes, SQL/Python reconciliation and independent source-total verification.
- **No fabricated business impact:** the deliverable is a shortlist for investigation, not a claim of revenue or client savings.

## Scope

| Dimension | Selection |
|---|---|
| Fiscal years | 2023, 2024, 2025; US fiscal years run October–September |
| Award types | Contracts: A, B, C, D |
| Agency basis | Awarding agency, top tier |
| Agencies | Veterans Affairs; Health and Human Services; Energy; NASA |
| NAICS | 541511 custom programming; 541512 systems design; 541519 other computer-related services |
| Measure | Nominal USD net transaction obligations, aggregated by recipient entity and fiscal year |
| Source snapshot | 1 October 2026 UTC; historical source revisions remain possible |

The agencies are a deliberate educational comparison set, not a representative statistical sample. The categories are broad IT services, not separate AI, cloud or cybersecurity markets. FY2026 is excluded because the year just ended and reporting can lag.

## Reproduce the results

Python **3.10 or later**; no third-party libraries needed. From the repository folder:

```bash
python src/analyze.py
python -m unittest discover -s tests -v
```

On Windows use `py` instead of `python` if needed. The included snapshot supports both commands offline. To collect missing raw files or independently cross-check latest-year totals:

```bash
python src/fetch_data.py
python src/reconcile_source.py
```

The fetcher reuses cached files. See [the beginner handbook](docs/START_TO_FINISH.md) before attempting a full refresh. Live API access requires internet and can take several minutes. The pipeline never substitutes simulated data after a network error.

## Main outputs

| File | What it contains |
|---|---|
| `index.html` | Offline interactive decision dashboard |
| `data/processed/market.db` | SQLite database with source table and analytical views |
| `data/processed/recipient_year.csv` | Cleaned recipient-year observations |
| `data/processed/annual_segments.csv` | Segment spending and concentration by year |
| `data/processed/opportunity_ranking.csv` | Score, components and rank stability |
| `data/processed/sensitivity.csv` | Full four-scenario rankings |
| `reports/DECISION_MEMO.md` | Generated consulting recommendation |
| `reports/data_quality.json` | Pipeline validation results |
| `reports/source_reconciliation.json` | Latest-year independent agency aggregation checks |

## Scoring in one sentence

Eligible segments receive **35% size + 35% growth + 30% fragmentation**, after within-scope min–max normalization; size uses log-transformed latest-year net obligations, growth uses FY2023–FY2025 CAGR and fragmentation uses `1 − HHI`. Latest-year net obligations must be at least $10m, with valid growth and concentration measures.

Weights and the $10m floor are explicit case assumptions. Scores are not probabilities, causal estimates or forecasts. Supplier shares use positive recipient-net values; negative values remain in net spending totals. Corporate parents are not consolidated, so concentration can be understated relative to parent-level concentration.

## Learn, explain, extend

1. [Start-to-finish beginner handbook](docs/START_TO_FINISH.md)
2. [Methodology and metric definitions](docs/METHODOLOGY.md)
3. [Data dictionary](docs/DATA_DICTIONARY.md)
4. [Code walkthrough](docs/CODE_WALKTHROUGH.md)
5. [Interview preparation](docs/INTERVIEW_GUIDE.md)
6. [Source register](docs/SOURCES.md)
7. [Power BI build instructions](docs/POWER_BI.md)
8. [GitHub upload and dashboard publishing](docs/GITHUB_GUIDE.md)

## Validation status

Ten Python tests passed. Dashboard calculations and controls were exercised using Node DOM stubs, and the static result chart was visually inspected. Full browser rendering was not verified in the build environment. See [validation details](reports/VALIDATION.md).

## Limitations and next steps

No eligibility, contract vehicle access, open solicitation, profit margin, win probability or delivery-fit data is included. Recipient entities may share a parent. Revisions and API pagination over a changing source can affect extracts; latest-year totals are independently checked. There are only three annual observations, so no forecasting or machine-learning accuracy is claimed.

A useful next extension is to validate the three shortlisted segments against actual procurement access and firm capability, then decide whether to pursue them. More modeling is not automatically better evidence.

## License and provenance

Project code and original documentation: MIT. Public data: [USAspending](https://www.usaspending.gov/), with its own source terms. Original API requests, retrieval timestamps and responses are retained. See [sources](docs/SOURCES.md).
