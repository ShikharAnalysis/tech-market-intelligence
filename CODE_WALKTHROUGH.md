# Code walkthrough

## Architecture

`config.json` → `src/fetch_data.py` → saved API JSON → `src/analyze.py` → CSV + SQLite + memo + `index.html`.

`sql/analysis.sql` is executed inside the pipeline. `src/reconcile_source.py` checks latest-year totals against another endpoint. `tests/test_analysis.py` checks important arithmetic and snapshot invariants. The dashboard embeds processed data; opening it sends no API request.

## fetch_data.py

`ROOT` uses the source file location so paths work even if you launch the script from elsewhere. `fetch_segment` builds a single query scope. The `filters` dictionary selects contract types, dates, agency and category. `urllib.request.Request` sends JSON using POST.

The pagination loop collects every page. `hasNext` controls termination, not an assumption that page one contains everything. Four attempts allow temporary failures; increasing waits reduce repeated pressure. If retries fail, the exception is visible.

A completed query writes to a temporary file before replacing the target. This prevents an interrupted write from looking complete. Cached completed segments are reused. After all jobs finish, SHA-256 hashes record the byte content of each raw file.

Concurrency speeds independent queries; it does not change analytical results. There are no credentials in the code because these public endpoints do not require authentication.

## analyze.py

`cents` uses Decimal to avoid binary floating-point surprises when converting dollars to cents. Monetary sums happen in integers. This cannot remove numerical artifacts already present in source aggregates.

`concentration` retains only positive recipient-net values for shares, sorts them, calculates squared shares and top-five share. It returns missing values when no positive denominator exists. The separate market total still includes negatives.

`normalize` maps a list into 0–1. Identical values get 0.5, so no division by zero occurs. `rank_segments` first applies eligibility, then computes the three components and weighted score. A deterministic secondary sort resolves exact ties by agency and NAICS.

`main` verifies hashes, coverage, pages and grain before computing anything. It creates cleaned rows, annual aggregates, current-year metrics and four scenario rankings. All tables are written to CSV for inspection. SQLite views calculate spending and concentration independently from the same cleaned rows; assertions compare SQL and Python results.

The memo is generated from the actual ranking. The dashboard receives the same JSON payload, reducing the risk of reporting a hand-typed number that differs from the model.

## analysis.sql

`segment_annual` groups source observations and sums cents. `recipient_shares` uses a partitioned sum for each denominator and `ROW_NUMBER` to identify the largest recipients. `concentration` joins those shares to segment totals and sums squared shares and top-five shares.

These are views: saved queries over the source table, not separate copies of the underlying data. When the table is rebuilt, the views reflect it.

## render_dashboard.py and dashboard_template.html

Python inserts the processed JSON into a self-contained HTML template. The JSON escapes `<` before insertion. Browser JavaScript handles interactions, recalculates scores from existing normalized components and draws SVG charts. It never fetches live data.

The agency filter is display-only. Changing it cannot alter the original scoring comparison set. Weight sliders normalize to a total of one, and an explicit fallback handles all-zero input. CSV export reflects the current score and shown agencies. Fixed-scenario robustness columns remain tied to the original four scenarios.

The dashboard uses standard HTML, CSS, JavaScript and SVG. Its absence of package dependencies simplifies sharing and reduces setup friction. It is not a Power BI or Streamlit app.

## reconcile_source.py

For each category it queries the awarding-agency endpoint for FY2025, then compares each selected agency's returned total with the sum built from recipient groups. Results are cached in `data/validation`. The check uses the documented half-cent-per-group rounding allowance and preserves actual differences. It is a check against an alternative aggregation path, not an independent external source.

## Tests worth understanding

Equal suppliers should give HHI `1 / supplier_count`. Negative amounts should never produce negative supplier shares. A zero positive denominator should produce missing concentration. Identical normalization values should not crash. A segment below the eligibility floor should not win just because its growth is large. Changing all weight to size versus growth should change a deliberately constructed test ranking.

The fabricated small values in tests are mathematical fixtures only. They are never mixed with the real analysis dataset.
