import copy
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from tiktok_pipeline import pipeline as p
from tiktok_pipeline.publish import credentials
from daily.catalog import episodes

class PipelineTests(unittest.TestCase):
    def test_three_local_slots(self):
        for when, schedule, key in [((11,7),'7 11 * * *','2026-09-16-01'),((17,7),'7 17 * * *','2026-09-16-02'),((23,7),'7 23 * * *','2026-09-16-03')]:
            self.assertEqual(p.resolve(datetime(2026,9,16,*when,tzinfo=timezone.utc),schedule), key)

    def test_delayed_run_keeps_planned_slot(self):
        # 08h atrasado quatro horas ainda vale para o horário 1 do mesmo dia
        self.assertEqual(p.resolve(datetime(2026,9,16,15,tzinfo=timezone.utc),'7 11 * * *'), '2026-09-16-01')
        # 20h do dia 16 que só começa 01h30 do dia 17 continua sendo do dia 16
        self.assertEqual(p.resolve(datetime(2026,9,17,4,30,tzinfo=timezone.utc),'7 23 * * *'), '2026-09-16-03')

    def test_topics_rotate_within_day(self):
        topics = {p.topic_for(f'2026-09-16-0{slot}') for slot in (1, 2, 3)}
        self.assertEqual(len(topics), 3)

    def test_old_slots_rejected(self):
        with self.assertRaises(ValueError):
            p.identity('2026-09-16', 4)

    def test_late_run_stops(self):
        with self.assertRaises(ValueError):
            p.resolve(datetime(2026,9,16,17,tzinfo=timezone.utc),'0 11 * * *')

    def test_bad_keys(self):
        for key in ['../secrets', '2026-09-16-06', '2026-02-30-01', None]:
            with self.assertRaises(ValueError): p.valid_key(key)

    def test_missing_auth_fails_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError): credentials()

    def test_cookie_domain_filter(self):
        cookies=[{'name':'sessionid','value':'test','domain':'.tiktok.com','path':'/'},
                 {'name':'other','value':'test','domain':'evil.example','path':'/'}]
        with patch.dict(os.environ, {'TIKTOK_COOKIES_JSON':json.dumps(cookies)}):
            self.assertEqual(len(credentials()), 1)

    def test_resume_never_regenerates(self):
        with tempfile.TemporaryDirectory() as d, patch.object(p,'HISTORY',Path(d)):
            p.save('2026-09-16-01', {'state':'submitted'})
            with patch('daily.new_script.api', side_effect=AssertionError('must not call')):
                self.assertEqual(p.prepare('2026-09-16-01')['state'],'submitted')

    def test_uncertain_send_blocks_render(self):
        with tempfile.TemporaryDirectory() as d, patch.object(p,'HISTORY',Path(d)):
            for state in ['unknown','uploading','submitted','published']:
                p.save('2026-09-16-01',{'state':state})
                with self.assertRaises(RuntimeError): p.render('2026-09-16-01')

    def test_catalog_reserved_and_repeats_rejected(self):
        ep=next(episodes())
        response={'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(ep)}]}]}
        with tempfile.TemporaryDirectory() as d, patch.object(p,'ROOT',Path(d)), patch.object(p,'HISTORY',Path(d)/'tt'), patch.dict(os.environ,{'PABLO_SCRIPT_MODEL':'test','TIKTOK_PILOT':'false'}):
            with patch('daily.new_script.api',return_value=response) as api:
                with self.assertRaises(RuntimeError): p.prepare('2026-09-16-01')
                # 3 tentativas x 2 rodadas de revisão de estilo (write_script)
                self.assertEqual(api.call_count,6)
            self.assertFalse((Path(d)/'tt').exists())

    def test_pilot_does_not_write_instagram_history(self):
        with tempfile.TemporaryDirectory() as d, patch.object(p,'ROOT',Path(d)), patch.object(p,'HISTORY',Path(d)/'tt'), patch.dict(os.environ,{'TIKTOK_PILOT':'true'}):
            item=p.prepare('2026-09-16-01')
            self.assertEqual(item['state'],'scripted')
            self.assertFalse((Path(d)/'history').exists())
            self.assertTrue(item['episode']['segments'][0]['text'].endswith('? Escute isso.'))

if __name__=='__main__': unittest.main()