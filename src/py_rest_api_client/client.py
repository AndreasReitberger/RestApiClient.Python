"""Reusable synchronous and asynchronous REST API client."""

import asyncio
import json
import os
import time
from collections import namedtuple
from typing import Any, Callable, Dict, Mapping, Optional, Type
from urllib.parse import urljoin, urlparse

import requests

from .exceptions import RestApiHttpError, RestApiNetworkError


RestApiRequestResponse = namedtuple(
    "RestApiRequestResponse",
    "status_code reason headers result content url elapsed response",
)


class RestApiClient(object):
    """Base class for API-specific clients.

    Subclass this class and add endpoint methods that call ``send_request``.
    The requests.Session is reused for connection pooling.  ``result`` in the
    returned response contains decoded JSON when possible, otherwise text.
    """

    _instance = None

    def __init__(self, base_url="", headers=None, auth=None, timeout=30,
                 verify=True, session=None, max_retries=0, retry_backoff=0.25,
                 rate_limit_per_second=None, raise_for_status=False):
        self.base_url = (base_url or "").rstrip("/") + ("/" if base_url else "")
        self.headers = dict(headers or {})
        self.auth = auth
        self.timeout = timeout
        self.verify = verify
        self.session = session or requests.Session()
        self.max_retries = max(0, int(max_retries))
        self.retry_backoff = max(0.0, float(retry_backoff))
        self.rate_limit_per_second = rate_limit_per_second
        self.raise_for_status = raise_for_status
        self._last_request_at = 0.0

    @classmethod
    def set_instance(cls, instance):
        """Set a process-wide convenience instance for the calling subclass."""
        cls._instance = instance

    @classmethod
    def get_instance(cls):
        """Return the process-wide convenience instance, if configured."""
        return cls._instance

    @classmethod
    def instance(cls):
        """Compatibility accessor for code that prefers ``Client.instance()``."""
        return cls.get_instance()

    def build_url(self, path="", url_segments=None, query=None):
        """Build an endpoint URL; ``{name}`` path tokens use url_segments."""
        path = str(path or "")
        if url_segments:
            if isinstance(url_segments, Mapping):
                path = path.format(**url_segments)
            else:
                path = path.format(*url_segments)
        parsed = urlparse(path)
        url = path if parsed.scheme else urljoin(self.base_url, path.lstrip("/"))
        return url

    def send_request(self, method, path="", params=None, headers=None, json_body=None,
                     data=None, files=None, auth=None, timeout=None, verify=None,
                     url_segments=None, expected_type=None, serializer=None,
                     raise_for_status=None, **request_options):
        """Send an HTTP request and return a RestApiRequestResponse.

        ``expected_type`` may be a class or callable applied to decoded JSON.
        ``serializer`` can convert custom objects to JSON-compatible values.
        Additional keyword arguments are forwarded to ``requests``.
        """
        url = self.build_url(path, url_segments, params)
        merged_headers = dict(self.headers)
        merged_headers.update(headers or {})
        if json_body is not None:
            if serializer:
                json_body = serializer(json_body)
            elif hasattr(json_body, "to_dict"):
                json_body = json_body.to_dict()
        if self.rate_limit_per_second:
            interval = 1.0 / float(self.rate_limit_per_second)
            delay = interval - (time.monotonic() - self._last_request_at)
            if delay > 0:
                time.sleep(delay)
        started = time.monotonic()
        attempt = 0
        while True:
            try:
                response = self.session.request(
                    method=method.upper(), url=url, params=params,
                    headers=merged_headers, json=json_body, data=data, files=files,
                    auth=self.auth if auth is None else auth,
                    timeout=self.timeout if timeout is None else timeout,
                    verify=self.verify if verify is None else verify,
                    **request_options
                )
                self._last_request_at = time.monotonic()
                break
            except requests.RequestException as exc:
                if attempt >= self.max_retries:
                    raise RestApiNetworkError(str(exc)) from exc
                time.sleep(self.retry_backoff * (2 ** attempt))
                attempt += 1
        try:
            result = response.json()
        except (ValueError, json.JSONDecodeError):
            result = response.text
        if expected_type is not None and result is not None:
            if isinstance(result, dict) and isinstance(expected_type, type):
                try:
                    result = expected_type(**result)
                except TypeError:
                    result = expected_type(result)
            else:
                result = expected_type(result)
        wrapped = RestApiRequestResponse(
            response.status_code, response.reason, response.headers, result,
            response.content, response.url, time.monotonic() - started, response
        )
        should_raise = self.raise_for_status if raise_for_status is None else raise_for_status
        if should_raise and not response.ok:
            raise RestApiHttpError(wrapped)
        return wrapped

    def get(self, path="", **kwargs):
        return self.send_request("GET", path, **kwargs)

    def post(self, path="", **kwargs):
        return self.send_request("POST", path, **kwargs)

    def put(self, path="", **kwargs):
        return self.send_request("PUT", path, **kwargs)

    def patch(self, path="", **kwargs):
        return self.send_request("PATCH", path, **kwargs)

    def delete(self, path="", **kwargs):
        return self.send_request("DELETE", path, **kwargs)

    def send_json_request(self, method, path="", body=None, **kwargs):
        """Send a JSON request body and accept a JSON response."""
        return self.send_request(method, path, json_body=body, **kwargs)

    def send_multipart_request(self, method, path="", files=None, data=None, **kwargs):
        """Send multipart form data, including file handles accepted by requests."""
        return self.send_request(method, path, files=files, data=data, **kwargs)

    def upload_file(self, path, file_path, field_name="file", method="POST", **kwargs):
        """Upload a file as multipart form data, closing the handle afterwards."""
        with open(file_path, "rb") as stream:
            return self.send_request(method, path,
                                     files={field_name: (os.path.basename(file_path), stream)},
                                     **kwargs)

    def download_file(self, path, destination, params=None, headers=None, **kwargs):
        """Download the response body to a file; returns its response wrapper."""
        response = self.send_request("GET", path, params=params, headers=headers, **kwargs)
        with open(destination, "wb") as stream:
            stream.write(response.content)
        return response

    async def send_request_async(self, method, path="", **kwargs):
        """Async wrapper for applications that use asyncio (Python 3.7+)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.send_request(method, path, **kwargs)
        )

    async def get_async(self, path="", **kwargs):
        return await self.send_request_async("GET", path, **kwargs)

    async def post_async(self, path="", **kwargs):
        return await self.send_request_async("POST", path, **kwargs)

    async def put_async(self, path="", **kwargs):
        return await self.send_request_async("PUT", path, **kwargs)

    async def delete_async(self, path="", **kwargs):
        return await self.send_request_async("DELETE", path, **kwargs)

    def close(self):
        """Close the underlying connection pool."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
