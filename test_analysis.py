import json, math, sqlite3, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from analyze import cents, concentration, normalize, rank_segments

class MetricTests(unittest.TestCase):
    def test_currency_is_exact(self):
        self.assertEqual(cents('123.45'),12345)
        self.assertEqual(cents('-0.01'),-1)
    def test_equal_supplier_shares(self):
        h,t=concentration([100]*10)
        self.assertAlmostEqual(h,.1);self.assertAlmostEqual(t,.5)
    def test_negative_net_not_a_market_share(self):
        h,t=concentration([100,100,-150,0]);self.assertAlmostEqual(h,.5);self.assertEqual(t,1)
    def test_no_positive_recipients(self):self.assertEqual(concentration([-2,0]),(None,None))
    def test_identical_values_neutral(self):self.assertEqual(normalize([7,7]),[.5,.5])
    def test_ineligible_excluded(self):
        rows=[{'agency':'A','naics':'1','net_obligations':100,'cagr':.1,'hhi':.2},
              {'agency':'B','naics':'1','net_obligations':9,'cagr':8,'hhi':.1}]
        self.assertEqual(len(rank_segments(rows,{'size':1,'growth':1,'fragmentation':1},10)),1)
    def test_preferences_change_ranking(self):
        rows=[{'agency':'A','naics':'1','net_obligations':100,'cagr':.1,'hhi':.2},
              {'agency':'B','naics':'1','net_obligations':50,'cagr':.5,'hhi':.1}]
        self.assertEqual(rank_segments(rows,{'size':1,'growth':0,'fragmentation':0},10)[0]['agency'],'A')
        self.assertEqual(rank_segments(rows,{'size':0,'growth':1,'fragmentation':0},10)[0]['agency'],'B')
    def test_invalid_weights_fail(self):
        row={'agency':'A','naics':'1','net_obligations':100,'cagr':.1,'hhi':.2}
        with self.assertRaises(ValueError):rank_segments([row],{'size':0,'growth':0,'fragmentation':0},10)

class SnapshotTests(unittest.TestCase):
    def test_sql_totals_and_row_count(self):
        db=sqlite3.connect(ROOT/'data/processed/market.db')
        raw=db.execute('SELECT SUM(obligation_cents),COUNT(*) FROM recipient_year').fetchone()
        rollup=db.execute('SELECT SUM(net_cents) FROM segment_annual').fetchone()[0]
        self.assertEqual(raw[0],rollup)
        q=json.loads((ROOT/'reports/data_quality.json').read_text())
        self.assertEqual(raw[1],q['recipient_year_rows']);db.close()
    def test_snapshot_scope_and_metrics(self):
        d=json.loads((ROOT/'data/processed/dashboard_data.json').read_text())
        self.assertEqual(len(d['annual']),36)
        self.assertEqual(d['quality']['missing_recipient_ids'],0)
        for r in d['ranking']:
            self.assertTrue(0<=r['score']<=100)
            self.assertTrue(0<r['hhi']<=1)
            self.assertTrue(0<r['top5_share']<=1.00000001)
            self.assertTrue(0<=r['top3_scenarios']<=4)
if __name__=='__main__':unittest.main()
