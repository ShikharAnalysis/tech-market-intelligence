# Source register and provenance

Prepared 1 October 2026. The authoritative evidence for computed numbers is the saved API snapshot, not a search snippet or a market-research estimate.

| Source | Use | URL |
|---|---|---|
| USAspending API endpoint documentation | Public API and endpoint definitions | https://api.usaspending.gov/docs/endpoints |
| USAspending introductory tutorial | POST requests and agency filters | https://api.usaspending.gov/docs/intro-tutorial |
| USAspending recipient aggregation | Primary analytical observations | https://api.usaspending.gov/api/v2/search/spending_by_category/recipient/ |
| USAspending agency aggregation | Latest-year total reconciliation | https://api.usaspending.gov/api/v2/search/spending_by_category/awarding_agency/ |
| US Census NAICS resources | Industry code labels and scope | https://www.census.gov/naics/ |
| US Census 2022 NAICS manual | Classification reference | https://www.census.gov/naics/reference_files_tools/2022_NAICS_Manual.pdf |
| GitHub documentation | Upload and Pages instructions | https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site |
| Microsoft Learn | Optional Power BI import workflow | https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-connect-to-data |

## Snapshot audit trail

The 36 raw query files include the exact request body for every page and retrieval timestamps. The manifest records SHA-256 file hashes. `data/validation` stores three supplementary agency queries. `reports/data_quality.json` and `reports/source_reconciliation.json` summarize checks. Actual source numbers are never replaced with generated examples.

## Refresh and interpretation

USAspending can revise prior periods. This repository reports the saved snapshot, not a permanently current market estimate. All source downloads occurred on the UTC date above. Public agency names and public recipient legal-entity names are used only to analyze published procurement data. No private client dataset was used.

## Original analysis versus source facts

Source-derived: recipient amounts, agencies, NAICS, fiscal-year filters and recipient identifiers.

Derived calculations: growth, concentration, relative score and sensitivity rank.

Analyst assumptions: selected scope, $10m floor, weights, scenario choices, hypothetical client and proposed next steps.

Not measured: procurement eligibility, margin, future opportunities, win probability, revenue improvement and client impact. These distinctions should remain visible when the project is shared.
