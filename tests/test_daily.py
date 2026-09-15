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
    def test_old_or_incomplete_hooks_are_rejected(self):
        import copy
        for text in ['Pablo Guru, por que tenho medo?', 'O medo te paralisa?', 'Escute isso.', 'O medo te paralisa. Escute isso.']:
            ep=copy.deepcopy(next(episodes()))
            ep['segments'][0]['text']=text
            with self.subTest(text=text), self.assertRaises(AssertionError):
                validate(ep)

    def test_hook_reaches_every_studio_episode(self):
        from daily.studio_adapter import roteiro
        for ep in episodes():
            ep['date']='2026-09-16'
            script=roteiro(ep)
            self.assertTrue(script['hook_first'])
            self.assertEqual(script['cenas'][0]['texto'],ep['segments'][0]['text'])
            self.assertEqual(script['cenas'][1]['texto'],ep['segments'][1]['text'])

    def test_exhaustion_does_not_repeat(self):
        with self.assertRaises(ValueError):select('2027-01-01')
    def test_before_start(self):
        with self.assertRaises(ValueError):select('2026-09-12')

if __name__=='__main__':unittest.main()
