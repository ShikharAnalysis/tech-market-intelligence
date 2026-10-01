-- SQLite. Grain: fiscal year × awarding agency × NAICS × recipient entity.
-- Money is stored as integer cents. Negative recipient net obligations remain.
DROP VIEW IF EXISTS concentration;
DROP VIEW IF EXISTS recipient_shares;
DROP VIEW IF EXISTS segment_annual;
CREATE VIEW segment_annual AS
SELECT fiscal_year,agency,naics, SUM(obligation_cents) AS net_cents,
       COUNT(*) AS recipients,
       SUM(CASE WHEN obligation_cents>0 THEN obligation_cents ELSE 0 END) AS positive_net_cents
FROM recipient_year GROUP BY fiscal_year,agency,naics;

CREATE VIEW recipient_shares AS
SELECT fiscal_year,agency,naics,recipient_id,recipient_name,obligation_cents,
       1.0*obligation_cents/SUM(obligation_cents) OVER (PARTITION BY fiscal_year,agency,naics) AS share,
       ROW_NUMBER() OVER (PARTITION BY fiscal_year,agency,naics ORDER BY obligation_cents DESC,recipient_id) AS position
FROM recipient_year WHERE obligation_cents>0;

CREATE VIEW concentration AS
SELECT a.fiscal_year,a.agency,a.naics,
       SUM(s.share*s.share) AS hhi,
       SUM(CASE WHEN s.position<=5 THEN s.share ELSE 0 END) AS top5_share
FROM segment_annual a LEFT JOIN recipient_shares s
ON a.fiscal_year=s.fiscal_year AND a.agency=s.agency AND a.naics=s.naics
GROUP BY a.fiscal_year,a.agency,a.naics;

-- Open market.db in DB Browser for SQLite and run these independently:
-- SELECT * FROM segment_annual ORDER BY fiscal_year DESC,net_cents DESC;
-- SELECT * FROM concentration WHERE fiscal_year=2025 ORDER BY hhi;
-- SELECT *, LAG(net_cents) OVER (PARTITION BY agency,naics ORDER BY fiscal_year) AS prior_year_cents FROM segment_annual;
-- SELECT * FROM recipient_shares WHERE fiscal_year=2025 AND position<=5;
