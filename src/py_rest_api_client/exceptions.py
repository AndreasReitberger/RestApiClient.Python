"""Exception types raised by the client."""


class RestApiClientError(Exception):
    """Base class for client errors."""


class RestApiNetworkError(RestApiClientError):
    """The request could not be completed due to a transport error."""


class RestApiHttpError(RestApiClientError):
    """An HTTP response indicated failure; the response is available as an attribute."""

    def __init__(self, response):
        self.response = response
        super(RestApiHttpError, self).__init__(
            "HTTP {} {}".format(response.status_code, response.reason)
        )
