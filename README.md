# PyRestApiClient

A reusable REST client inspired by the C# [RestApiClientSharp](https://github.com/AndreasReitberger/RestApiClientSharp). It targets Python 3.7 and later and provides common request handling for API-specific client libraries.

## Install

```bash
python install_dependencies.py
```

The installer checks for Python 3.7+, pins the runtime and build dependencies in `requirements.txt`, and installs this checkout in editable mode. The pins keep Python 3.7 compatible, including pip 24.0, setuptools 67.8.0, wheel 0.42.0 and requests 2.31.0.

## Build package files

After installing the dependencies, create both a wheel and a source archive with:

```bash
python build_package.py
```

The generated files are placed in `dist/`.

## Quick start

```python
from py_rest_api_client import RestApiClient


class ExampleApi(RestApiClient):
    def __init__(self, token):
        super(ExampleApi, self).__init__(
            "https://api.example.com/v1",
            headers={"Authorization": "Bearer " + token},
            timeout=20,
            max_retries=2,
        )

    def get_item(self, item_id):
        return self.get("items/{id}", url_segments={"id": item_id}).result

    def create_item(self, item):
        return self.post("items", json_body=item).result


api = ExampleApi("your-token")
item = api.get_item(42)
```

## Features

- GET, POST, PUT, PATCH and DELETE methods, with sync calls and asyncio wrappers.
- Base URL composition, path segments and query parameters.
- Shared and per-request headers, basic auth and arbitrary `requests` options.
- JSON request serialization and JSON response decoding, with optional model conversion.
- Multipart form requests and convenience file upload/download methods.
- Optional retry with exponential backoff, request rate limiting and HTTP error raising.
- A response wrapper exposing status, headers, decoded result, raw bytes, URL, elapsed time and the underlying `requests.Response`.
- Reusable sessions with context-manager and explicit close support.

Async methods run synchronous `requests` calls in an executor: they work with asyncio but do not provide a native asynchronous HTTP transport. For an API-specific library, subclass `RestApiClient` and add endpoint methods as in the example.

```python
response = api.get("items", params={"page": 2})
if response.status_code == 200:
    print(response.result)

# asyncio
# item = await api.get_async("items/42")
```

The package source lives under `src/py_rest_api_client`. It requires `requests` and is intended to remain compatible with Python 3.7.

## Integration check

The live integration test makes a read-only request to the public JSONPlaceholder API:

```bash
python -m unittest discover -s tests -v
```

If the API cannot be reached from the current environment, the test is reported as skipped.
