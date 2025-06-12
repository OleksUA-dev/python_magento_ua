"""Базові винятки для Magento Python бібліотеки."""

from typing import Any, Optional


class MagentoError(Exception):
    """Базовий виняток для всіх помилок Magento бібліотеки."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error

    def __str__(self) -> str:
        if self.original_error:
            return f"{self.message} (caused by: {self.original_error})"
        return self.message


class MagentoAPIError(MagentoError):
    """Базовий виняток для всіх API помилок."""
    pass


class MagentoNetworkError(MagentoError):
    """Базовий виняток для мережевих помилок."""
    pass


class MagentoConfigurationError(MagentoError):
    """Виняток для помилок конфігурації."""
    pass


class MagentoValidationError(MagentoError):
    """Виняток для помилок валідації."""
    pass


class MagentoSecurityError(MagentoError):
    """Виняток для проблем безпеки."""
    pass