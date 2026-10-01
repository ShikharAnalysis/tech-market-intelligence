# Validation record

- Python metric and snapshot tests: 10 passed.
- Raw query hashes, scope, unique keys and pagination: passed.
- SQL/Python integer-cent totals: exact agreement.
- SQL/Python HHI and top-five shares: agreement within numerical tolerance.
- Separate agency aggregation: 12 latest-year segments within the documented rounding allowance; maximum absolute difference $0.04.
- Dashboard JavaScript: baseline and growth-scenario scores agree with Python; agency filter, zero-weight fallback, CSV handler and finite SVG coordinates checked in Node with minimal DOM stubs.
- Static results chart: rendered and visually inspected.
- Full browser visual and layout test: not completed because the execution environment blocks the browser's socket operations. DOM-stub testing does not validate browser layout, downloads or accessibility end to end.

Reproduce with `python src/analyze.py`, `python -m unittest discover -s tests -v`, and optionally `node tests/test_dashboard.cjs` (Node 18+). The Python pipeline needs no Node installation. A full live-source check additionally uses `python src/reconcile_source.py`.
