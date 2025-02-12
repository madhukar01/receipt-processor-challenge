import os

import redis
from pottery import NextId
from pottery import RedisDict


# Read redis host from env
REDIS_URL: str = os.getenv(
    key="REDIS_URL",
    default="redis://127.0.0.1:6379/0",
)


class Redis:
    """
    Redis cache store
    This module is used to store key values in the cache store.
    """

    def __init__(self, namespace: str) -> None:
        """
        Connect to redis client

        Args:
            namespace: Namespace for key isolation

        Raises:
            ValueError: If namespace is invalid
            ConnectionError: If unable to connect to redis
        """
        redis_client = redis.from_url(REDIS_URL)

        # Validate string namespace
        if not isinstance(namespace, str):
            raise ValueError("Invalid namespace")

        namespace = namespace.strip()
        if not namespace:
            raise ValueError("Invalid namespace")
        self.__namespace = namespace

        # Check if client is connected to redis
        if not redis_client.ping():
            raise ConnectionError("Unable to connect to redis")

        self.__client: redis.Redis = redis_client

    def is_connected(self) -> bool:
        """
        Check if client is connected to redis

        Returns:
            bool: True if connected else False
        """
        return self.__client.ping()

    def get_key(self, key: str) -> str | None:
        """
        Fetch value for the key from redis cache

        Args:
            key: Key to fetch value for

        Returns:
            str | None: Value for the key if exists, None otherwise
        """
        # Validate string key
        if not isinstance(key, str):
            return None

        key = key.strip()
        if not key:
            return None

        # Attach namespace to key
        key = f"{self.__namespace}_{key}"
        value = self.__client.get(key)
        return value.decode("utf-8") if value else None

    def set_key(self, key: str, value: str) -> bool | None:
        """
        Set value for the key in redis cache without expiration

        Args:
            key: Key to set value for
            value: Value to set

        Returns:
            bool | None: True if set successfully, None otherwise

        Raises:
            ValueError: If parameters are invalid
        """
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("Invalid parameter types")

        key = key.strip()
        value = value.strip()
        if not key or not value:
            raise ValueError("Invalid parameter values")

        # Attach namespace to key
        key = f"{self.__namespace}_{key}"
        return self.__client.set(name=key, value=value)

    def set_expiring_key(
        self,
        key: str,
        value: str,
        expire: int = 300,
    ) -> bool | None:
        """
        Set value for the key in redis cache with an expiration time

        Args:
            key: Key to set value for
            value: Value to set
            expire: Expire time in seconds (minimum 1 second, maximum 1 day)

        Returns:
            bool | None: True if set successfully, None otherwise

        Raises:
            ValueError: If parameters are invalid
        """
        if (
            not isinstance(key, str)
            or not isinstance(value, str)
            or not isinstance(expire, int)
        ):
            raise ValueError("Invalid parameter types")

        key = key.strip()
        value = value.strip()
        if not key or not value or not 0 < expire < 86400:
            raise ValueError("Invalid parameter values")

        # Attach namespace to key
        key = f"{self.__namespace}_{key}"
        return self.__client.setex(name=key, value=value, time=expire)

    def delete_key(self, key: str) -> int | None:
        """
        Delete key:value from redis cache

        Args:
            key: Key to delete

        Returns:
            int | None: Number of keys deleted, None if error

        Raises:
            ValueError: If key is invalid
        """
        if not isinstance(key, str):
            raise ValueError("Invalid key type")

        key = key.strip()
        if not key:
            raise ValueError("Invalid key value")

        # Attach namespace to key
        key = f"{self.__namespace}_{key}"
        return self.__client.delete(key)

    def get_dictionary(self, key: str) -> RedisDict:
        """
        Get a dictionary stored in redis

        Args:
            key: Key to get dictionary for

        Returns:
            RedisDict: Dictionary for the key

        Raises:
            ValueError: If key is invalid
        """
        if not isinstance(key, str):
            raise ValueError("Invalid key type")

        key = key.strip()
        if not key:
            raise ValueError("Invalid key value")

        # Attach namespace to key
        key = f"{self.__namespace}_{key}"
        return RedisDict(key=key, redis=self.__client)

    def get_id_generator(self, key: str) -> NextId:
        """
        Get a unique ID generator

        Args:
            key: Key for the ID generator

        Returns:
            NextId: ID generator instance

        Raises:
            ValueError: If key is invalid
        """
        if not isinstance(key, str):
            raise ValueError("Invalid key type")

        key = key.strip()
        if not key:
            raise ValueError("Invalid key value")

        # Attach namespace to key
        key = f"{self.__namespace}_{key}"
        return NextId(key=key, masters={self.__client})
