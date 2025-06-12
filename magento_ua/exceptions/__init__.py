"""Експорт всіх винятків для зручності імпорту."""

# Базові винятки
from .base import (
    MagentoError,
    MagentoAPIError,
    MagentoNetworkError,
    MagentoConfigurationError,
    MagentoValidationError,
    MagentoSecurityError,
)

# API винятки
from .api import (
    APIError,
    HTTPError,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    UnprocessableEntityError,
    TooManyRequestsError,
    InternalServerError,
    BadGatewayError,
    ServiceUnavailableError,
    GatewayTimeoutError,
    AuthenticationError,
    TokenExpiredError,
    InvalidTokenError,
    ValidationError,
    ResourceNotFoundError,
    ProductNotFoundError,
    OrderNotFoundError,
    CustomerNotFoundError,
    CategoryNotFoundError,
    RateLimitExceededError,
    StoreNotFoundError,
    InsufficientPermissionsError,
    create_http_exception,
    STATUS_CODE_EXCEPTIONS,
)

# Мережеві винятки
from .network import (
    NetworkError,
    ConnectionError,
    TimeoutError,
    RetryExhaustedError,
    ProxyError,
    SSLError,
)

# Список всіх доступних винятків для import *
__all__ = [
    # Базові
    "MagentoError",
    "MagentoAPIError",
    "MagentoNetworkError",
    "MagentoConfigurationError",
    "MagentoValidationError",
    "MagentoSecurityError",

    # API
    "APIError",
    "HTTPError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
    "TooManyRequestsError",
    "InternalServerError",
    "BadGatewayError",
    "ServiceUnavailableError",
    "GatewayTimeoutError",
    "AuthenticationError",
    "TokenExpiredError",
    "InvalidTokenError",
    "ValidationError",
    "ResourceNotFoundError",
    "ProductNotFoundError",
    "OrderNotFoundError",
    "CustomerNotFoundError",
    "CategoryNotFoundError",
    "RateLimitExceededError",
    "StoreNotFoundError",
    "InsufficientPermissionsError",
    "create_http_exception",
    "STATUS_CODE_EXCEPTIONS",

    # Мережеві
    "NetworkError",
    "ConnectionError",
    "TimeoutError",
    "RetryExhaustedError",
    "ProxyError",
    "SSLError",
]