"""General purpose REST API client helpers (Python 3.7+)."""

from .client import RestApiClient, RestApiRequestResponse
from .exceptions import RestApiClientError, RestApiHttpError, RestApiNetworkError

__all__ = [
    "RestApiClient",
    "RestApiRequestResponse",
    "RestApiClientError",
    "RestApiHttpError",
    "RestApiNetworkError",
]

__version__ = "0.1.0"
