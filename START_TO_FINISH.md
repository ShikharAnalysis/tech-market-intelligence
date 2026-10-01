# Start-to-finish handbook for Shikhar

This guide assumes you are still learning Python and SQL. You do not need to understand every line before opening the dashboard. You do need to understand the business question, the data and the calculations before presenting this as a project you can defend.

## Stage 1 — Understand what the project does

Imagine a consulting firm's manager says: “We cannot chase every government technology market. Which three segments should we investigate first?”

Your role is to make that choice more evidence-based. You collect historical spending, organize it into comparable segments, measure growth and supplier concentration, and show how the shortlist changes under different business priorities. You finish with a recommendation and a plan to validate it.

**The decision is where to investigate, not where revenue is guaranteed.** This distinction is central to the project.

A segment is one agency and one service category, such as Veterans Affairs × custom computer programming. A recipient is an entity receiving an award. Net obligations are committed dollars after relevant adjustments. A fiscal year is a reporting year; US FY2025 runs from October 2024 through September 2025.

## Stage 2 — Open the delivered project

1. Download the ZIP and extract it to a convenient location, such as Documents.
2. Open the `tech-market-intelligence` folder.
3. Double-click `index.html`. It opens in your browser and does not need internet.
4. Read the opening question and the scope labels.
5. Change “Balanced” to “Growth first.” Observe the leader and scores.
6. Filter to Energy. Notice that displayed ranks retain their position in the full comparison set.
7. Hover over a bubble to read the segment's values.
8. Download the ranking CSV and open it in Excel if available.
9. Read `reports/DECISION_MEMO.md`. GitHub will render Markdown; a text editor can also open it.

You have now reviewed the finished product. Next, learn how it was generated.

## Stage 3 — Set up Python on Windows

Use Python 3.10 or later from the official Python website. During installation, enable the option to add Python to PATH if shown. You can also use the Windows Python launcher, `py`.

Open the project folder in File Explorer, click the address bar, type `cmd` and press Enter. This opens a command prompt in the correct folder.

Check the installation:

```bat
py --version
```

Run the analysis:

```bat
py src\analyze.py
```

Run the checks:

```bat
py -m unittest discover -s tests -v
```

On macOS/Linux, use `python3 src/analyze.py` and `python3 -m unittest discover -s tests -v`. No package installation is needed because the project uses Python's standard library.

Expected outcome: analysis prints the quality summary and leading segment; tests report success. The analysis overwrites generated CSVs, database, memo and dashboard using the included source snapshot. It does not contact the API.

## Stage 4 — Follow one observation through the system

Open any JSON file in `data/raw`. At the top you will find its source URL, retrieval time, agency, NAICS category and fiscal year. Under `pages`, find `request`, then `response`, then `results`.

Choose one recipient result. Its `amount` is the recipient's net obligations for the query, not necessarily one contract. Find the same entity in `data/processed/recipient_year.csv`, using its UEI or API identity. The amount appears as integer cents: divide `obligation_cents` by 100 to obtain USD.

Now open `annual_segments.csv`. Find the row for that agency/category/year. Its net obligations equal the sum of all recipient amounts in the group, including negative amounts. The pipeline did not discard negative values to inflate the total.

Finally open `opportunity_ranking.csv`. Locate that agency/category for FY2025. Read its growth, concentration, component values, score and sensitivity range. This is the full path from source to decision.

## Stage 5 — Learn the SQL through small questions

The file `data/processed/market.db` is a SQLite database. You can open it with DB Browser for SQLite or another SQLite client. A database is simply an organized way to store and query tables.

Start with five rows:

```sql
SELECT * FROM recipient_year LIMIT 5;
```

Count observations:

```sql
SELECT COUNT(*) AS recipient_year_records FROM recipient_year;
```

Understand the reporting grain:

```sql
SELECT fiscal_year, agency, naics, COUNT(*) AS recipient_groups
FROM recipient_year
GROUP BY fiscal_year, agency, naics
ORDER BY fiscal_year, agency, naics;
```

Find the largest FY2025 segments:

```sql
SELECT agency, naics, SUM(obligation_cents) / 100.0 AS net_usd
FROM recipient_year
WHERE fiscal_year = 2025
GROUP BY agency, naics
ORDER BY net_usd DESC;
```

Inspect negative groups:

```sql
SELECT fiscal_year, agency, recipient_name, obligation_cents / 100.0 AS net_usd
FROM recipient_year
WHERE obligation_cents < 0
ORDER BY obligation_cents
LIMIT 10;
```

Show the top five positive recipients in each FY2025 segment:

```sql
SELECT agency, naics, recipient_name, share, position
FROM recipient_shares
WHERE fiscal_year = 2025 AND position <= 5
ORDER BY agency, naics, position;
```

Compare consecutive years:

```sql
SELECT fiscal_year, agency, naics, net_cents / 100.0 AS net_usd,
       LAG(net_cents / 100.0) OVER (
         PARTITION BY agency, naics ORDER BY fiscal_year
       ) AS previous_year_usd
FROM segment_annual;
```

`GROUP BY` collapses observations into groups. `SUM` adds values. `WHERE` filters input rows. A window function such as `LAG` looks at related rows without collapsing them. `PARTITION BY` defines those related rows. Explain these ideas using this dataset instead of memorizing definitions.

## Stage 6 — Learn the Python you actually need

Read `docs/CODE_WALKTHROUGH.md` beside the source files. Focus on:

- Dictionaries: named values such as an agency, year or amount.
- Lists: collections of recipients or segments.
- Loops: performing the same operation for every row.
- Functions: reusable calculations such as concentration or normalization.
- File reading: loading JSON and writing CSV.
- Validation: stopping when the data does not meet expectations.

Try a hand calculation. If three suppliers have positive net values of 50, 30 and 20, their shares are 0.5, 0.3 and 0.2. HHI is 0.25 + 0.09 + 0.04 = 0.38. If a fourth recipient has −10, total net obligations become 90, but the positive-recipient denominator used for HHI remains 100. Explain why a negative market share would be nonsensical.

Then calculate a two-year CAGR. Growing from 100 to 144 over two years gives `(144/100)^(1/2) − 1 = 20%`. It does not mean every year actually grew by 20%.

## Stage 7 — Interpret the recommendation

Read all three shortlisted segments, not just the first. For each ask:

1. Is it large, growing, fragmented, or a combination?
2. Does the latest-year movement agree with the two-year CAGR?
3. What changes when priorities change?
4. Are the five largest recipients dominant?
5. What essential business information is missing?

Avoid “this is the best market.” Say “this segment ranks highest within our selected scope and assumptions, so it deserves further qualification.” That is more precise and more credible.

Write your own 150-word conclusion after reviewing the dashboard. State the decision, two supporting facts, the main limitation and the next action. Add it as `docs/MY_INTERPRETATION.md` when you are ready. This personal interpretation is intentionally not written for you.

## Stage 8 — Refresh or change the analysis safely

`fetch_data.py` caches completed raw files, so simply running it again does not overwrite existing snapshots. That preserves reproducibility.

For a full new snapshot, make a separate copy of the entire project folder. In that copy, move the old `data/raw` and `data/validation` directories to an archive outside the project. Recreate empty directories with those names. Run:

```bat
py src\fetch_data.py
py src\analyze.py
py src\reconcile_source.py
py -m unittest discover -s tests -v
```

Keep all four commands in that order. Internet is needed for the first and third. If a download fails, rerun the fetcher; completed segment files are reused. Never manually create a fake manifest to bypass a failure.

For a simple learning exercise, change only the scoring weights in `config.json`, keeping the same three keys and nonnegative values with a positive total. Run the analysis again and compare rankings. The currently supplied dashboard's named presets use fixed 35/35/30 and 60/20/20 variants; if you change the intended baseline, update those presets and methodology too.

Adding agencies/categories requires new complete downloads and source verification. Changing years also requires adapting dashboard labels, chart positions and snapshot tests; this package intentionally targets three specific years. Do not assume the dashboard is a generic arbitrary-period platform.

## Stage 9 — Optional Power BI version

The complete delivered dashboard is HTML. A native `.pbix` file is not included. If you want Power BI practice, follow `docs/POWER_BI.md` to import the processed CSVs and build a second presentation layer. Do not list Power BI as a completed project tool until you actually build that version.

## Stage 10 — Publish the repository

Follow `docs/GITHUB_GUIDE.md`. Upload the extracted project contents, not just the ZIP. The root must contain `README.md` and `index.html`. Check that the data and source folders arrived. Open the README, inspect the result chart and confirm the analysis workflow passes.

GitHub Pages is an optional way to share the static dashboard. The repository and dashboard serve different purposes: the repository shows your process; the dashboard lets a reviewer explore the decision quickly.

## Stage 11 — Prepare for the interview

Use `docs/INTERVIEW_GUIDE.md`. Practice explaining the business question in one sentence, the dataset grain in one sentence and the biggest limitation in one sentence. Then explain one SQL query and one function without reading a script.

Be honest about AI assistance and your own changes. If you did not independently implement a component, do not pretend you did. You can still demonstrate competence by reproducing the results, explaining them, identifying limitations and making a meaningful, tested improvement.

A reasonable practice sequence, not a promised learning timeline:

| Session | Task | Evidence you understood it |
|---|---|---|
| 1 | Explore dashboard and memo | Explain the recommendation in your words |
| 2 | Inspect one raw record and CSV | Explain the unit of observation |
| 3 | Run the SQL examples | Recreate a group total |
| 4 | Study HHI, CAGR and score | Calculate a small example by hand |
| 5 | Run pipeline and tests | Explain what a failure would mean |
| 6 | Change a weighting assumption | Explain how and why rankings change |
| 7 | Add your interpretation and publish | Give a three-minute walkthrough |

## Troubleshooting

**“Python was not found.”** Try `py` on Windows or `python3` on macOS/Linux. Check installation and reopen the terminal.

**“No such file.”** Your terminal is not in the project folder. Navigate to the folder containing `config.json` and `src`.

**“Hash mismatch.”** A raw file differs from its recorded snapshot. Restore the original from the ZIP or perform a clean refresh. Do not edit the hash merely to silence the check.

**API timeout/429/5xx.** The upstream service may be slow or rate-limited. Included data still works offline. Retry later; do not increase concurrency aggressively.

**Scores differ after a change.** Verify weights, eligibility floor, source snapshot and normalization scope. A new source snapshot can revise old fiscal years.

**SQL reports no table.** Open `data/processed/market.db`, not an empty database you just created. Rebuild it with `analyze.py` if necessary.

**CSV columns look wrong.** Import with comma delimiter and UTF-8 encoding. Keep NAICS and recipient IDs as text. Percentages are stored as decimal fractions.

**Pages shows README instead of dashboard.** Confirm `index.html` is at the selected publishing root and the deployment finished.
