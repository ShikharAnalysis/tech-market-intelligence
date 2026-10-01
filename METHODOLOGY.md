# Methodology: from spending records to a research shortlist

## 1. Decision and unit of analysis

The hypothetical client is a mid-sized IT consulting firm researching public-sector expansion. Its immediate decision is where to allocate exploratory business-development effort, not which contract to bid on. The unit to rank is **awarding agency × NAICS service category**. Twelve segments are compared.

The four agencies create a deliberately bounded case covering health, energy and space-related public buyers. They were not selected using a formal sampling design or to establish that they are the best agencies nationwide. Three related NAICS codes create interpretable service segments. Excluded agencies and codes can contain larger or better opportunities.

## 2. Source and grain

Official USAspending endpoint: `/api/v2/search/spending_by_category/recipient/`.

Filters: award types A/B/C/D; one top-tier awarding agency; one NAICS code; one complete US fiscal year; spending level `transactions`. Fiscal year 2025 means 1 October 2024 through 30 September 2025. This is **not** a sum of lifetime award values for awards that happened to be active in a year.

Each downloaded result is a recipient's net transaction obligations within that query. One cleaned row therefore represents **FY × agency × NAICS × recipient entity**. It is not an individual contract, transaction or customer. Do not say “7,704 contracts” when describing the delivered snapshot.

Recipient identity uses UEI where provided, otherwise API recipient ID, then API ID. Names receive whitespace cleanup only; punctuation matching never merges different legal entities. Unknown identity has a visible fallback and quality counter. The supplied snapshot has no missing IDs. Subsidiaries sharing a parent remain separate.

## 3. Ingestion and completeness

The downloader pages until `hasNext` is false, uses up to four concurrent queries, retries failed requests with bounded exponential backoff and writes each segment atomically. Requests, responses and UTC retrieval times are retained. The manifest hashes each complete raw file. Analysis checks expected segment coverage, sequential pages, final-page completion, duplicate keys and hashes.

A failure stops the run; partial data is never relabeled as complete and no mock data is substituted. Pagination occurs against a live, potentially changing source rather than an atomic database snapshot. Capture times expose that limitation.

## 4. Net obligations and negative values

Obligations are commitments, not actual cash outlays, revenue, profit or total contract ceilings. Negative amounts can arise from deobligations and corrections. We retain negative recipient-year net values when summing the market.

The API has already netted transactions within each recipient. A positive recipient-net value may itself contain both positive and negative transactions. Therefore the positive sum is called **positive recipient net obligations**, never “gross obligations.” This extract cannot calculate gross transaction commitments or transaction-level deobligations.

Money is converted with Decimal to integer cents before storage and summation. Presentation exports use USD. Ratios and normalized scores use floating-point arithmetic. No inflation adjustment is applied.

## 5. Metrics

Let n(i,t) be recipient i's net obligations in a segment in year t.

- Net segment obligations: `N(t) = sum(n(i,t))`, including negative amounts.
- Positive-recipient base: `P(t) = sum(max(n(i,t), 0))`.
- Positive recipient share: `s(i,t) = max(n(i,t),0) / P(t)`.
- HHI: `sum(s(i,t)^2)`, scale 0–1. It is undefined when P is zero.
- Top-five share: sum of the five largest positive shares, or all if fewer than five exist.
- CAGR: `(N(2025)/N(2023))^(1/2) − 1`, only when both endpoints are positive.
- YoY: `N(2025)/N(2024) − 1`, only when the previous year is positive.

HHI measures concentration among recorded recipient entities, not competitive intensity directly. A low HHI does not establish an easy market. Parent aggregation, acquisition history and procurement vehicles could alter the interpretation.

## 6. Eligibility and score

Screen only segments with latest-year net obligations at least $10m and valid CAGR and HHI. This floor is an analyst-selected case assumption that reduces attention to very small segments; it is not a Gartner benchmark.

Components before normalization:

1. Size = `ln(1 + latest-year net obligations)` in USD.
2. Growth = two-year CAGR.
3. Fragmentation = `1 − HHI`.

Each component is min–max scaled across eligible segments: `(value − minimum) / (maximum − minimum)`. When all values are equal the component receives 0.5 for every segment. Log size moderates the influence of very large segments; it does not add forecasting power.

Score = `100 × (0.35 × size_component + 0.35 × growth_component + 0.30 × fragmentation_component)`.

The maximum possible score is 100; a score of 70 is **not** a 70% chance of winning. Min–max scaling is sensitive to the comparison set and outliers. Adding an agency can change existing scores. There is no causal inference or machine learning in this model.

Dashboard filters only hide or show agencies. They do not rescale components. Weights change the score; the ranking remains global across eligible segments, so filtered ranks can have gaps. All-zero dashboard weights explicitly fall back to equal weights.

## 7. Sensitivity analysis

Four fixed scenarios: balanced (35/35/30), size-led (60/20/20), growth-led (20/60/20), fragmentation-led (20/20/60). Report rank range and number of appearances in the top three. These scenarios express different preferences. They are not random draws, a statistical confidence interval or an estimated probability.

The dashboard's custom scenario is separate from the fixed four-scenario robustness columns. No retrospective prediction test is claimed. Only three annual observations are available; fitting a forecasting model would give an unjustified impression of predictive certainty.

## 8. Validation

- SHA-256 integrity against the supplied raw manifest.
- Expected coverage of 36 queries; pagination and unique-grain validation.
- SQL and Python spend totals reconcile exactly in integer cents.
- SQL and Python HHI and top-five shares match within numerical tolerance.
- Latest-year recipient sums cross-checked against a separate awarding-agency aggregation endpoint for all 12 segments.

For the last check, a recipient-level sum can differ from a separately rounded aggregate. The tolerance is **$0.005 × (recipient count + 1)**, the worst-case accumulation of half-cent rounding per displayed input plus the separately rounded total. We report actual differences as well as pass/fail and do not overwrite them. In this snapshot differences range from $0 to $0.04 in absolute terms. These are consistent with numerical aggregation/rounding differences; their precise upstream cause is not proven. A material mismatch fails the check and requires investigation.

Checks are technical validation, not certification of government reporting accuracy. Independent aggregation reconciliation currently covers FY2025 only.

## 9. Recommendation gates

The top three are priorities for further research. Before pursuing a market, verify internal capability, security and location requirements, registration, procurement vehicles, set-asides, upcoming solicitations, delivery partners and sales cost. A quantitative leader can fail those gates. Do not interpret the shortlist as advice that an individual in India can immediately bid for those contracts.

## 10. Boundaries and honest claims

Historical obligations do not reveal the next tender, incumbent renewals, margin, addressable spend, customer satisfaction or attainable market share. The project does not estimate any of these. Any future financial case must label assumptions and collect additional evidence. Results may change after a source refresh. This is a screening tool and an educational consulting case, not a market forecast or a Gartner research publication.
