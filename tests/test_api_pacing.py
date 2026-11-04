import unittest
from unittest.mock import Mock, patch

from investigation.agents.groq_client import GroqClient
from investigation.runtime import InvestigationRuntime


class ApiPacingTests(unittest.TestCase):
    def setUp(self):
        environment = patch.dict('os.environ', {'GROQ_API_KEY': 'test-key'})
        environment.start()
        self.addCleanup(environment.stop)

    def test_first_call_is_immediate_then_waits_remaining_interval(self):
        with patch('config.settings.GROQ_MIN_CALL_INTERVAL_SECONDS', 60):
            client = GroqClient()
        response = Mock(ok=True)
        response.json.return_value = {'choices': [{'message': {'content': 'answer'}}]}
        with patch('requests.post', return_value=response) as post:
            with patch('investigation.agents.groq_client.monotonic', side_effect=[100, 110, 160]):
                with patch('investigation.agents.groq_client.sleep') as sleep:
                    client.generate('first')
                    sleep.assert_not_called()
                    client.generate('second')
                    sleep.assert_called_once_with(50)
        self.assertEqual(post.call_count, 2)
        self.assertEqual(client.last_call_started_at, 160)

    def test_no_wait_when_interval_already_elapsed(self):
        client = GroqClient()
        client.last_call_started_at = 100
        with patch('investigation.agents.groq_client.monotonic', return_value=170):
            with patch('investigation.agents.groq_client.sleep') as sleep:
                client.wait_before_call()
                sleep.assert_not_called()

    def test_disabled_interval(self):
        with patch('config.settings.GROQ_MIN_CALL_INTERVAL_SECONDS', 0):
            client = GroqClient()
        client.last_call_started_at = 100
        with patch('investigation.agents.groq_client.monotonic', return_value=100):
            with patch('investigation.agents.groq_client.sleep') as sleep:
                client.wait_before_call()
                sleep.assert_not_called()

    def test_invalid_interval(self):
        for value in (-1, float('nan'), float('inf')):
            with patch('config.settings.GROQ_MIN_CALL_INTERVAL_SECONDS', value):
                with self.assertRaises(ValueError):
                    GroqClient()

    def test_default_budget_is_configurable_and_override_is_preserved(self):
        with patch('config.settings.INVESTIGATION_MAX_DURATION_SECONDS', 600):
            self.assertEqual(InvestigationRuntime(Mock(), Mock()).max_duration_seconds, 600)
            self.assertEqual(InvestigationRuntime(Mock(), Mock(), max_duration_seconds=20).max_duration_seconds, 20)


if __name__ == '__main__':
    unittest.main()
