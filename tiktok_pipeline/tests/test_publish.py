import hashlib
import importlib
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

pub = importlib.import_module('tiktok_pipeline.publish')

class UploadTests(unittest.TestCase):
    def test_no_send_without_remote_intent(self):
        with patch.object(pub,'credentials',return_value=[]), patch.object(pub,'read',return_value={'state':'validated'}):
            with self.assertRaisesRegex(RuntimeError,'uploading'):
                pub.publish('2026-09-16-01')

    def test_failed_confirmation_is_unknown_and_never_retried(self):
        key='2026-09-16-01'
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/key).mkdir()
            (root/key/'episodio.mp4').write_bytes(b'test video')
            (root/key/'legenda.txt').write_text('Teste')
            item={'state':'uploading','video_hash':hashlib.sha256(b'test video').hexdigest()}
            page=MagicMock()
            page.get_by_role.return_value.get_attribute.return_value='/@opabloguru'
            button=MagicMock(); confirmation=MagicMock()
            confirmation.wait_for.side_effect=TimeoutError('uncertain')
            page.locator.side_effect=[button,confirmation]
            playwright=MagicMock()
            playwright.return_value.__enter__.return_value.chromium.launch.return_value.new_context.return_value.new_page.return_value=page
            upstream=types.ModuleType('tiktok_uploader.upload')
            upstream.config=types.SimpleNamespace(selectors=types.SimpleNamespace(upload=types.SimpleNamespace(post='post',post_confirmation='confirmed')))
            upstream._post_video=MagicMock()
            upstream._set_interactivity=MagicMock()
            client=MagicMock()
            client.upload_video.side_effect=lambda **kw: upstream._post_video(page)
            upstream.TikTokUploader=MagicMock(return_value=client)
            parent=types.ModuleType('tiktok_uploader'); parent.upload=upstream
            sync=types.ModuleType('playwright.sync_api'); sync.sync_playwright=playwright
            modules={'tiktok_uploader':parent,'tiktok_uploader.upload':upstream,'playwright':types.ModuleType('playwright'),'playwright.sync_api':sync}
            with patch.dict('sys.modules',modules), patch.object(pub,'OUT',root), patch.object(pub,'credentials',return_value=[]), patch.object(pub,'read',return_value=item), patch.object(pub,'save') as save:
                with self.assertRaises(RuntimeError): pub.publish(key)
                self.assertEqual(item['state'],'unknown')
                self.assertEqual(button.click.call_count,1)
                save.assert_called_once_with(key,item)
