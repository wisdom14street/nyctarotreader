"""The live checker must fail safely rather than report an unverified release."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

spec = importlib.util.spec_from_file_location('site_release', Path(__file__).resolve().parents[1] / 'scripts/release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        (root / 'site').mkdir()
        (root / 'site/config.json').write_text(json.dumps({'domain': 'nyctarotreader.com'}))
        self.root_patch = patch.object(release, 'ROOT', root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def test_refuses_external_origin_without_request(self):
        with patch.object(release, 'read') as read:
            with self.assertRaises(ValueError):
                release.verify('https://namastebookshop.com', 'expected')
            read.assert_not_called()

    def test_does_not_retry_rate_limit(self):
        error = HTTPError('https://nyctarotreader.com/release.json', 429, 'Rate limited', {}, None)
        with patch.object(release, 'read', side_effect=error) as read, patch.object(release.time, 'sleep') as sleep:
            with self.assertRaises(HTTPError):
                release.verify('https://nyctarotreader.com', 'expected')
            self.assertEqual(read.call_count, 1)
            sleep.assert_not_called()

    def test_rejects_wrong_release(self):
        with patch.object(release, 'read', return_value=b'{"commit":"older"}'), patch.object(release.time, 'sleep'):
            with self.assertRaisesRegex(ValueError, 'expected release is not live'):
                release.verify('https://nyctarotreader.com', 'expected')

    def test_rejects_modified_page(self):
        manifest = {'commit': 'expected', 'files': {'cart/index.html': release.digest(b'correct'), 'assets/ga.js': release.digest(b'script')}}
        with patch.object(release, 'read', side_effect=[json.dumps(manifest).encode(), b'wrong']):
            with self.assertRaisesRegex(ValueError, 'Published file differs'):
                release.verify('https://nyctarotreader.com', 'expected')
