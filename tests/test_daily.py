import unittest
from datetime import date,timedelta
from daily.catalog import episodes
from daily.prepare import select,validate

class DailyTests(unittest.TestCase):
    def test_bank_and_unique_dates(self):
        bank=list(episodes());seen=set()
        for i,ep in enumerate(bank):
            validate(ep)
            day=(date(2026,9,13)+timedelta(days=i)).isoformat()
            chosen=select(day)
            self.assertEqual(chosen,ep)
            self.assertNotIn(chosen['id'],seen);seen.add(chosen['id'])
            self.assertEqual(chosen,select(day))
    def test_exhaustion_does_not_repeat(self):
        with self.assertRaises(ValueError):select('2027-01-01')
    def test_before_start(self):
        with self.assertRaises(ValueError):select('2026-09-12')

if __name__=='__main__':unittest.main()
