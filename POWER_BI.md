# Optional Power BI implementation

The delivered working dashboard is `index.html`. This guide is an optional learning extension; **no native PBIX file is included**.

## Import

In Power BI Desktop, choose **Get data → Text/CSV**. Import `annual_segments.csv`, `opportunity_ranking.csv` and `sensitivity.csv` from `data/processed`. Use Power Query to verify numeric types; keep agency, category and NAICS as text. Rename tables to `Annual`, `Ranking` and `Sensitivity` for the measures below.

These are already aggregated analytical tables. Keep them disconnected initially and use each table for its own visuals. Do not create many-to-many relationships on agency alone: that can duplicate numbers. A later star schema should use distinct segment keys and a year dimension.

## Measures

```dax
Net Obligations = SUM(Annual[net_obligations])

FY2025 Net Obligations =
CALCULATE([Net Obligations], Annual[fiscal_year] = 2025)

Ranked Segments = COUNTROWS(Ranking)
```

Format obligations as currency USD. Format `cagr`, `yoy` and `top5_share` as percentages. Format HHI as a decimal, not a percentage. Do not sum HHI, CAGR or scores across segments. Use “Don't summarize” at segment grain or an appropriate selected-value measure.

## Build a one-page report

1. Cards: FY2025 net obligations and count of ranked segments.
2. Line chart from Annual: fiscal year on X, net obligations on Y, segment on legend; filter to a few segments to avoid clutter.
3. Scatter from Ranking: HHI on X, CAGR on Y, net obligations for bubble size, agency/category identifying each point.
4. Table from Ranking: rank, agency, category, obligations, CAGR, HHI, score, top-three scenario count.
5. Matrix from Sensitivity: segment rows, scenario columns, rank as the value at a unique segment/scenario grain.
6. Add visible source, scope and methodology notes.

In Power Query, create a display segment column by combining agency and NAICS. If you later add shared slicers, create a distinct segment dimension and explicit one-to-many relationships. Test totals after every relationship change.

The Python ranking is imported as a fixed calculation. Do not imply a Power BI slicer recalculates weights unless you implement and validate DAX parameters and scoring. The delivered HTML dashboard already supports weight changes.

Save your report as `MarketLens.pbix` only after completing it. Compare its table values with `opportunity_ranking.csv`. When those agree and your visuals are readable, it becomes an additional tool you can honestly discuss.

Official reference: [Connect to data in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-connect-to-data).
