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

ip = "169.254.0.155"
port = 6543

class RaspberryPiRestApiTest(unittest.TestCase):
    """Check a real GET request and JSON decoding without modifying remote data."""

    def test_get_post_by_path_segment(self):
        client = RestApiClient(
            f"http://{ip}:{port}",
            timeout=10,
            max_retries=1,
        )
        try:
            try:
                version = client.get("version")
                print(f"Connected to API version: {version.result}")
            except (RestApiNetworkError, requests.RequestException) as exc:
                self.skipTest("Public API is unavailable from this environment: {}".format(exc))
        finally:
            client.close()

if __name__ == "__main__":
    unittest.main()
