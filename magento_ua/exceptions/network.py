"""Мережеві винятки для Magento Python бібліотеки."""

from typing import Optional

from .base import MagentoNetworkError


class NetworkError(MagentoNetworkError):
    """Загальна мережева помилка."""
    pass


class ConnectionError(NetworkError):
    """Помилка з'єднання."""

    def __init__(
            self,
            message: str = "Connection failed",
            host: Optional[str] = None,
            port: Optional[int] = None,
            **kwargs
    ):
        super().__init__(message, **kwargs)
        self.host = host
        self.port = port

    def __str__(self) -> str:
        base_str = super().__str__()
        if self.host:
            connection_info = f"Host: {self.host}"
            if self.port:
                connection_info += f":{self.port}"
            return f"{base_str} ({connection_info})"
        return base_str


class TimeoutError(NetworkError):
    """Помилка тайм-ауту."""

    def __init__(
            self,
            message: str = "Request timeout",
            timeout_seconds: Optional[float] = None,
            **kwargs
    ):
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds

    def __str__(self) -> str:
        base_str = super().__str__()
        if self.timeout_seconds:
            return f"{base_str} (timeout: {self.timeout_seconds}s)"
        return base_str


class RetryExhaustedError(NetworkError):
    """Вичерпано всі спроби повторних запитів."""

    def __init__(
            self,
            message: str = "All retry attempts exhausted",
            max_retries: Optional[int] = None,
            last_error: Optional[Exception] = None,
            **kwargs
    ):
        super().__init__(message, **kwargs)
        self.max_retries = max_retries
        self.last_error = last_error

    def __str__(self) -> str:
        base_str = super().__str__()
        details = []

        if self.max_retries is not None:
            details.append(f"max retries: {self.max_retries}")

        if self.last_error:
            details.append(f"last error: {self.last_error}")

        if details:
            return f"{base_str} ({', '.join(details)})"
        return base_str


class ProxyError(NetworkError):
    """Помилка проксі сервера."""

    def __init__(
            self,
            message: str = "Proxy error",
            proxy_url: Optional[str] = None,
            **kwargs
    ):
        super().__init__(message, **kwargs)
        self.proxy_url = proxy_url

    def __str__(self) -> str:
        base_str = super().__str__()
        if self.proxy_url:
            return f"{base_str} (proxy: {self.proxy_url})"
        return base_str


class SSLError(NetworkError):
    """Помилка SSL/TLS."""

    def __init__(
            self,
            message: str = "SSL/TLS error",
            certificate_error: Optional[str] = None,
            **kwargs
    ):
        super().__init__(message, **kwargs)
        self.certificate_error = certificate_error

    def __str__(self) -> str:
        base_str = super().__str__()
        if self.certificate_error:
            return f"{base_str} (cert error: {self.certificate_error})"
        return base_str


class DNSError(NetworkError):
    """Помилка DNS resolution."""

    def __init__(
            self,
            message: str = "DNS resolution failed",
            hostname: Optional[str] = None,
            **kwargs
    ):
        super().__init__(message, **kwargs)
        self.hostname = hostname

    def __str__(self) -> str:
        base_str = super().__str__()
        if self.hostname:
            return f"{base_str} (hostname: {self.hostname})"
        return base_str


class RateLimitError(NetworkError):
    """Помилка перевищення ліміту швидкості."""

    def __init__(
            self,
            message: str = "Rate limit exceeded",
            retry_after: Optional[int] = None,
            requests_per_second: Optional[float] = None,
            **kwargs
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
        self.requests_per_second = requests_per_second

    def __str__(self) -> str:
        base_str = super().__str__()
        details = []

        if self.retry_after:
            details.append(f"retry after: {self.retry_after}s")

        if self.requests_per_second:
            details.append(f"limit: {self.requests_per_second} req/s")

        if details:
            return f"{base_str} ({', '.join(details)})"
        return base_str


class CircuitBreakerOpenError(NetworkError):
    """Circuit breaker відкритий - запити блокуються."""

    def __init__(
            self,
            message: str = "Circuit breaker is open",
            failure_count: Optional[int] = None,
            timeout_until: Optional[float] = None,
            **kwargs
    ):
        super().__init__(message, **kwargs)
        self.failure_count = failure_count
        self.timeout_until = timeout_until

    def __str__(self) -> str:
        base_str = super().__str__()
        details = []

        if self.failure_count:
            details.append(f"failures: {self.failure_count}")

        if self.timeout_until:
            details.append(f"retry after: {self.timeout_until}")

        if details:
            return f"{base_str} ({', '.join(details)})"
        return base_str


# Експорт для зручності
__all__ = [
    "NetworkError",
    "ConnectionError",
    "TimeoutError",
    "RetryExhaustedError",
    "ProxyError",
    "SSLError",
    "DNSError",
    "RateLimitError",
    "CircuitBreakerOpenError",
]