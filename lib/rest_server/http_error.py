from dataclasses import dataclass


@dataclass
class HTTPError:
    """
    HTTPError class represents an HTTP error

    Attributes:
        error_code: HTTP error code
        error_msg: HTTP error message
    """

    error_code: int
    error_msg: str
