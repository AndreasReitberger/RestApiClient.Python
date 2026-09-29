"""Opt-in live integration check against JSONPlaceholder's public API.

Run with: python -m unittest discover -s tests -v
"""

import unittest
import os
import sys

import requests

# Let the test run from a source checkout without requiring an editable install.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from py_rest_api_client import RestApiClient, RestApiNetworkError


class JsonPlaceholderIntegrationTest(unittest.TestCase):
    """Check a real GET request and JSON decoding without modifying remote data."""

    def test_get_post_by_path_segment(self):
        client = RestApiClient(
            "https://jsonplaceholder.typicode.com",
            timeout=10,
            max_retries=1,
        )
        try:
            try:
                response = client.get("posts/{post_id}", url_segments={"post_id": 1})
            except (RestApiNetworkError, requests.RequestException) as exc:
                self.skipTest("Public API is unavailable from this environment: {}".format(exc))

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.result["id"], 1)
            self.assertIn("title", response.result)
            self.assertTrue(response.url.endswith("/posts/1"))
        finally:
            client.close()


if __name__ == "__main__":
    unittest.main()
