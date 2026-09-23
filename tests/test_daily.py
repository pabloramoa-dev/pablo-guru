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

    def test_prop_matches_drawing_and_virada_is_spoken(self):
        from daily.studio_adapter import roteiro, PROP_DESENHO
        from daily.new_script import PROPS
        self.assertEqual(set(PROPS), set(PROP_DESENHO))
        for ep in episodes():
            ep['date']='2026-09-24'
            script=roteiro(ep)
            self.assertEqual(script['cenas'][1]['cenario'], PROP_DESENHO[ep['prop']])
            self.assertEqual(script['cenas'][5]['texto'], ep['segments'][5]['text'])
            self.assertEqual(script['cenas'][5]['falante'], 'pablo')
            self.assertTrue(script['cenas'][5].get('destaque'))
            self.assertEqual(script['cenas'][6]['anotacao'], ep['frase'])
            self.assertIn(script['capa']['paleta'], ['noite','vinho','petroleo','musgo','terracota'])

    def test_every_drawing_exists(self):
        import re
        from pathlib import Path
        from daily.studio_adapter import PROP_DESENHO
        src=(Path(__file__).resolve().parents[1]/'studio'/'pablo_cenarios.py').read_text(encoding='utf-8')
        cenarios=src[src.index('CENARIOS = {'):]
        for desenho in set(PROP_DESENHO.values()):
            self.assertIn(f'"{desenho}":', cenarios)

    def test_coach_style_is_rejected(self):
        import copy
        from daily.new_script import style_problems
        ep=copy.deepcopy(next(episodes()))
        ep['segments'][5]['text']='Na virada, desative uma notificação e liste três tarefas.'
        probs=style_problems(ep)
        self.assertTrue(any('coach' in p for p in probs))
        self.assertTrue(any('ponte' in p for p in probs))

    def test_caption_has_hook_note_and_tags(self):
        from daily.prepare import legenda
        ep=next(episodes())
        txt=legenda(ep)
        self.assertTrue(txt.startswith(ep['segments'][0]['text']))
        self.assertIn(ep['frase'], txt)
        self.assertIn('@opabloguru', txt)
        self.assertLessEqual(txt.count('#'), 10)

    def test_exhaustion_does_not_repeat(self):
        with self.assertRaises(ValueError):select('2027-01-01')
    def test_before_start(self):
        with self.assertRaises(ValueError):select('2026-09-12')

if __name__=='__main__':unittest.main()
