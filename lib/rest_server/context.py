from dataclasses import dataclass

import structlog

from lib.core.redis_connector import Redis


@dataclass
class Context:
    """
    Context class represents essential connectors for each request.

    Attributes:
        logger: structlog logger
        request_id: string request ID
        redis: Redis connector
    """

    logger: structlog.stdlib.AsyncBoundLogger
    request_id: str
    redis: Redis
