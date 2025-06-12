"""API-специфічні винятки для Magento REST API."""

from typing import Any, Dict, Optional

from .base import MagentoAPIError  # Виправлений імпорт


class APIError(MagentoAPIError):
    """Базовий виняток для API помилок."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}
        self.endpoint = endpoint

    def __str__(self) -> str:
        parts = [super().__str__()]

        if self.status_code:
            parts.append(f"Status: {self.status_code}")

        if self.endpoint:
            parts.append(f"Endpoint: {self.endpoint}")

        if self.response_data:
            error_message = self.response_data.get('message')
            if error_message and error_message != str(self):
                parts.append(f"API Message: {error_message}")

        return " | ".join(parts)


class HTTPError(APIError):
    """HTTP статус помилки (4xx, 5xx)."""
    pass


class BadRequestError(HTTPError):
    """HTTP 400 Bad Request."""

    def __init__(self, message: str = "Bad Request", **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class UnauthorizedError(HTTPError):
    """HTTP 401 Unauthorized."""

    def __init__(self, message: str = "Unauthorized", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class ForbiddenError(HTTPError):
    """HTTP 403 Forbidden."""

    def __init__(self, message: str = "Forbidden", **kwargs):
        super().__init__(message, status_code=403, **kwargs)


class NotFoundError(HTTPError):
    """HTTP 404 Not Found."""

    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class ConflictError(HTTPError):
    """HTTP 409 Conflict."""

    def __init__(self, message: str = "Conflict", **kwargs):
        super().__init__(message, status_code=409, **kwargs)


class UnprocessableEntityError(HTTPError):
    """HTTP 422 Unprocessable Entity."""

    def __init__(self, message: str = "Unprocessable Entity", **kwargs):
        super().__init__(message, status_code=422, **kwargs)


class TooManyRequestsError(HTTPError):
    """HTTP 429 Too Many Requests."""

    def __init__(self, message: str = "Too Many Requests", **kwargs):
        super().__init__(message, status_code=429, **kwargs)


class InternalServerError(HTTPError):
    """HTTP 500 Internal Server Error."""

    def __init__(self, message: str = "Internal Server Error", **kwargs):
        super().__init__(message, status_code=500, **kwargs)


class BadGatewayError(HTTPError):
    """HTTP 502 Bad Gateway."""

    def __init__(self, message: str = "Bad Gateway", **kwargs):
        super().__init__(message, status_code=502, **kwargs)


class ServiceUnavailableError(HTTPError):
    """HTTP 503 Service Unavailable."""

    def __init__(self, message: str = "Service Unavailable", **kwargs):
        super().__init__(message, status_code=503, **kwargs)


class GatewayTimeoutError(HTTPError):
    """HTTP 504 Gateway Timeout."""

    def __init__(self, message: str = "Gateway Timeout", **kwargs):
        super().__init__(message, status_code=504, **kwargs)


# Magento-специфічні помилки

class AuthenticationError(APIError):
    """Помилка аутентифікації Magento API."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, **kwargs)


class TokenExpiredError(AuthenticationError):
    """Токен доступу застарів."""

    def __init__(self, message: str = "Access token expired", **kwargs):
        super().__init__(message, **kwargs)


class InvalidTokenError(AuthenticationError):
    """Невалідний токен доступу."""

    def __init__(self, message: str = "Invalid access token", **kwargs):
        super().__init__(message, **kwargs)


class ValidationError(APIError):
    """Помилка валідації даних."""

    def __init__(
        self,
        message: str = "Validation failed",
        validation_errors: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.validation_errors = validation_errors or {}

    def __str__(self) -> str:
        base_str = super().__str__()
        if self.validation_errors:
            errors_str = ", ".join([
                f"{field}: {error}"
                for field, error in self.validation_errors.items()
            ])
            return f"{base_str} | Validation errors: {errors_str}"
        return base_str


class ResourceNotFoundError(NotFoundError):
    """Ресурс не знайдено в Magento."""

    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id

        if resource_id:
            message = f"{resource_type} with ID '{resource_id}' not found"
        else:
            message = f"{resource_type} not found"

        super().__init__(message, **kwargs)


class ProductNotFoundError(ResourceNotFoundError):
    """Товар не знайдено."""

    def __init__(self, product_id: Optional[str] = None, **kwargs):
        super().__init__("Product", product_id, **kwargs)


class OrderNotFoundError(ResourceNotFoundError):
    """Замовлення не знайдено."""

    def __init__(self, order_id: Optional[str] = None, **kwargs):
        super().__init__("Order", order_id, **kwargs)


class CustomerNotFoundError(ResourceNotFoundError):
    """Клієнта не знайдено."""

    def __init__(self, customer_id: Optional[str] = None, **kwargs):
        super().__init__("Customer", customer_id, **kwargs)


class CategoryNotFoundError(ResourceNotFoundError):
    """Категорія не знайдена."""

    def __init__(self, category_id: Optional[str] = None, **kwargs):
        super().__init__("Category", category_id, **kwargs)


class RateLimitExceededError(TooManyRequestsError):
    """Перевищено ліміт запитів."""

    def __init__(
        self,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        self.retry_after = retry_after
        message = "Rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"

        super().__init__(message, **kwargs)


class StoreNotFoundError(ResourceNotFoundError):
    """Store не знайдено."""

    def __init__(self, store_code: Optional[str] = None, **kwargs):
        super().__init__("Store", store_code, **kwargs)


class InsufficientPermissionsError(ForbiddenError):
    """Недостатньо прав для виконання операції."""

    def __init__(
        self,
        operation: Optional[str] = None,
        resource: Optional[str] = None,
        **kwargs
    ):
        self.operation = operation
        self.resource = resource

        message = "Insufficient permissions"
        if operation and resource:
            message += f" for {operation} on {resource}"
        elif operation:
            message += f" for {operation}"
        elif resource:
            message += f" for {resource}"

        super().__init__(message, **kwargs)


# Маппінг HTTP статус кодів до винятків
STATUS_CODE_EXCEPTIONS = {
    400: BadRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    422: UnprocessableEntityError,
    429: TooManyRequestsError,
    500: InternalServerError,
    502: BadGatewayError,
    503: ServiceUnavailableError,
    504: GatewayTimeoutError,
}


def create_http_exception(
    status_code: int,
    message: str,
    response_data: Optional[Dict[str, Any]] = None,
    endpoint: Optional[str] = None
) -> HTTPError:
    """Створити відповідний HTTP виняток за статус кодом."""
    exception_class = STATUS_CODE_EXCEPTIONS.get(status_code, HTTPError)

    return exception_class(
        message=message,
        status_code=status_code,
        response_data=response_data,
        endpoint=endpoint
)


# Експорт для зручності
__all__ = [
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
    "STATUS_CODE_EXCEPTIONS",
    "create_http_exception",
]