import unittest
from direct_guru.watchdog import Watchdog


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


class WatchdogTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.exits = []
        self.dog = Watchdog(request_limit=45, worker_limit=300, clock=self.clock,
                            exit_fn=lambda: self.exits.append(True))

    def test_request_tracked_and_released(self):
        seen = []

        def app(env, start_response):
            seen.append(self.dog.stuck())
            self.clock.now += 50
            seen.append(self.dog.stuck())
            start_response('200 OK', [])
            return [b'ok']

        out = self.dog.wrap(app)({'REQUEST_METHOD': 'POST', 'PATH_INFO': '/webhook', 'QUERY_STRING': 'hub.verify_token=x'}, lambda s, h: None)
        self.assertEqual(out, [b'ok'])
        self.assertIsNone(seen[0])
        self.assertIn('POST /webhook', seen[1])
        self.assertNotIn('verify_token', seen[1])
        self.assertIsNone(self.dog.stuck())

    def test_exception_releases_request(self):
        def app(env, start_response):
            raise ValueError('x')
        with self.assertRaises(ValueError):
            self.dog.wrap(app)({'PATH_INFO': '/webhook'}, lambda s, h: None)
        self.clock.now += 100
        self.assertFalse(self.dog.check_once())

    def test_stalled_queue_triggers_exit(self):
        self.dog.beat()
        self.clock.now += 299
        self.assertFalse(self.dog.check_once())
        self.clock.now += 2
        self.assertTrue(self.dog.check_once())
        self.assertEqual(self.exits, [True])

    def test_beat_resets(self):
        self.clock.now += 299
        self.dog.beat()
        self.clock.now += 299
        self.assertIsNone(self.dog.stuck())


if __name__ == '__main__':
    unittest.main()
