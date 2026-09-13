import os
import unittest
from unittest.mock import patch
from direct_guru.server import create_app

class SetupTests(unittest.TestCase):
    @patch.dict(os.environ, {'DIRECT_SETUP_ONLY':'true','DIRECT_ENABLED':'false'}, clear=True)
    def test_setup_never_accepts_webhooks(self):
        app=create_app()
        for path,expected in [('/health','200 OK'),('/webhook','503 Service Unavailable')]:
            statuses=[]
            app({'PATH_INFO':path}, lambda status,headers: statuses.append(status))
            self.assertEqual(statuses,[expected])

    @patch.dict(os.environ, {'DIRECT_SETUP_ONLY':'true','DIRECT_ENABLED':'true'}, clear=True)
    def test_setup_cannot_enable_delivery(self):
        with self.assertRaises(RuntimeError):create_app()
