# Data dictionary

## recipient_year.csv / SQLite recipient_year

Grain: fiscal year × awarding agency × NAICS × recipient entity. Primary key is those four identifiers.

| Field | Type | Meaning |
|---|---|---|
| fiscal_year | integer | US fiscal year of the filtered transactions |
| agency | text | Top-tier awarding agency name |
| naics | text | Six-digit service classification |
| category | text | Readable category label from configuration |
| recipient_id | text | UEI, otherwise API recipient identity fallback |
| recipient_name | text | Source entity name with whitespace cleaned |
| obligation_cents | integer | Net transaction obligations for this group, USD cents |
| source_file | text | Raw JSON containing this observation |

Do not count these rows as contracts or distinct recipients across the whole dataset. One recipient can appear in multiple agencies, categories and years.

## annual_segments.csv

Grain: fiscal year × agency × NAICS.

| Field | Unit / interpretation |
|---|---|
| net_obligations | USD, including negative recipient-net values |
| positive_recipient_net | Sum of positive recipient-net USD; not gross transaction commitments |
| negative_recipient_net | Sum of negative recipient-net USD; not all transaction deobligations |
| recipient_count | Number of recipient groups, including zero and negative groups |
| positive_recipients | Number with positive net obligations |
| hhi | Sum of squared positive recipient shares, 0–1 |
| top5_share | Top-five positive recipient shares, fraction 0–1 |

Identity and category fields carry through from the source grain.

## opportunity_ranking.csv

Grain: latest fiscal year × agency × NAICS, eligible segments only. Includes latest annual metrics plus:

| Field | Unit / interpretation |
|---|---|
| base_obligations | First-year net USD |
| cagr | Annualized endpoint growth as fraction, e.g. .2 = 20% |
| yoy | Latest year versus previous year growth as fraction |
| size_component | Normalized log size, 0–1 |
| growth_component | Normalized CAGR, 0–1 |
| fragmentation_component | Normalized 1−HHI, 0–1 |
| score | Weighted relative screening score, 0–100 |
| rank | Descending base-case score position |
| top3_scenarios | Count among four fixed scenarios, not probability |
| best_rank / worst_rank | Sensitivity rank range |

## sensitivity.csv

One row per eligible segment per fixed scenario: scenario name, agency, NAICS, rank and score. Never sum score across scenarios or segments.

## Quality and source files

`reports/data_quality.json`: snapshot times, row counts, negative-value counts and validation flags.

`reports/source_reconciliation.json`: alternative-aggregation difference, documented rounding tolerance, exact-match indicator and pass/fail per latest-year segment.

`data/raw/manifest.sha256.json`: hashes of source query files, excluding itself. `data/validation` contains supporting agency aggregation responses; it is separate from the 36 recipient-query manifest.

Missing numeric values appear blank in CSV and null in JSON. They are not automatically zero. Dates and source timestamps are UTC. All money is nominal USD, not INR.
