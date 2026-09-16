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
    def test_five_local_slots(self):
        for hour, schedule, slot in [(11,'0 11 * * *',1),(14,'0 14 * * *',2),(17,'0 17 * * *',3),(21,'0 21 * * *',4),(0,'0 0 * * *',5)]:
            expected = '2026-09-15' if hour == 0 else '2026-09-16'
            self.assertEqual(p.resolve(datetime(2026,9,16,hour,tzinfo=timezone.utc),schedule), f'{expected}-{slot:02d}')

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
                self.assertEqual(api.call_count,3)
            self.assertFalse((Path(d)/'tt').exists())

    def test_pilot_does_not_write_instagram_history(self):
        with tempfile.TemporaryDirectory() as d, patch.object(p,'ROOT',Path(d)), patch.object(p,'HISTORY',Path(d)/'tt'), patch.dict(os.environ,{'TIKTOK_PILOT':'true'}):
            item=p.prepare('2026-09-16-01')
            self.assertEqual(item['state'],'scripted')
            self.assertFalse((Path(d)/'history').exists())
            self.assertTrue(item['episode']['segments'][0]['text'].endswith('? Escute isso.'))

if __name__=='__main__': unittest.main()
