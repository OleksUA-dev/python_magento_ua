"""
Конфігурації для тестування Magento Python бібліотеки.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class TestConfig:
    """Базова конфігурація для тестів."""

    # Основні налаштування для тестів
    TEST_BASE_URL = "https://test-magento.example.com"
    TEST_USERNAME = "test_user"
    TEST_PASSWORD = "test_password"
    TEST_TIMEOUT = 10
    TEST_MAX_RETRIES = 1

    # Альтернативні тестові налаштування
    ALT_BASE_URL = "https://alt-test.example.com"
    ALT_USERNAME = "alt_user"
    ALT_PASSWORD = "alt_password"


class EnvironmentConfigs:
    """Різні конфігурації змінних оточення для тестів."""

    # Базова env конфігурація
    BASIC_ENV = {
        "MAGENTO_BASE_URL": "https://env.example.com",
        "MAGENTO_USERNAME": "env_user",
        "MAGENTO_PASSWORD": "env_pass",
        "MAGENTO_VERIFY_SSL": "false",
        "MAGENTO_TIMEOUT": "45"
    }

    # Повна env конфігурація
    FULL_ENV = {
        "MAGENTO_BASE_URL": "https://full-env.example.com",
        "MAGENTO_USERNAME": "full_env_user",
        "MAGENTO_PASSWORD": "full_env_password",
        "MAGENTO_VERIFY_SSL": "true",
        "MAGENTO_TIMEOUT": "60",
        "MAGENTO_MAX_RETRIES": "5",
        "MAGENTO_RATE_LIMIT": "200",
        "MAGENTO_ENABLE_CACHE": "true",
        "MAGENTO_CACHE_TTL": "7200",
        "MAGENTO_LOG_LEVEL": "DEBUG",
        "MAGENTO_LOG_FORMAT": "json"
    }

    # Env з шифруванням
    ENCRYPTION_ENV = {
        "MAGENTO_BASE_URL": "https://secure.example.com",
        "MAGENTO_USERNAME": "secure_user",
        "MAGENTO_PASSWORD": "secure_password",
        "MAGENTO_ENABLE_ENCRYPTION": "true",
        "MAGENTO_ENCRYPTION_KEY": "a" * 32  # 32-символьний ключ
    }

    # Env з проксі
    PROXY_ENV = {
        "MAGENTO_BASE_URL": "https://proxy-test.example.com",
        "MAGENTO_USERNAME": "proxy_user",
        "MAGENTO_PASSWORD": "proxy_password",
        "MAGENTO_PROXY_URL": "http://proxy.example.com:8080"
    }

    # Env для performance тестів
    PERFORMANCE_ENV = {
        "MAGENTO_BASE_URL": "https://perf-test.example.com",
        "MAGENTO_USERNAME": "perf_user",
        "MAGENTO_PASSWORD": "perf_password",
        "MAGENTO_TIMEOUT": "5",
        "MAGENTO_MAX_RETRIES": "1",
        "MAGENTO_RATE_LIMIT": "1000"
    }

    # Невалідні конфігурації для тестування помилок
    INVALID_ENV = {
        "MAGENTO_BASE_URL": "invalid-url",
        "MAGENTO_USERNAME": "",
        "MAGENTO_PASSWORD": "",
    }


class DictConfigs:
    """Словникові конфігурації для тестів."""

    # Мінімальна конфігурація
    MINIMAL = {
        "base_url": "https://minimal.example.com",
        "username": "minimal_user",
        "password": "minimal_password"
    }

    # Стандартна конфігурація
    STANDARD = {
        "base_url": "https://standard.example.com",
        "username": "standard_user",
        "password": "standard_password",
        "timeout": 30,
        "max_retries": 3,
        "verify_ssl": True,
        "rate_limit": 100
    }

    # Розширена конфігурація
    EXTENDED = {
        "base_url": "https://extended.example.com",
        "username": "extended_user",
        "password": "extended_password",
        "timeout": 60,
        "max_retries": 5,
        "verify_ssl": False,
        "rate_limit": 200,
        "enable_cache": True,
        "cache_ttl": 3600,
        "log_level": "DEBUG",
        "enable_metrics": True
    }

    # Конфігурація з усіма опціями
    COMPLETE = {
        "base_url": "https://complete.example.com",
        "username": "complete_user",
        "password": "complete_password",
        "verify_ssl": True,
        "timeout": 45,
        "max_retries": 4,
        "retry_delay": 2.0,
        "max_connections": 50,
        "max_keepalive_connections": 10,
        "rate_limit": 150,
        "rate_limit_window": 60,
        "proxy_url": "http://proxy.example.com:8080",
        "enable_cache": True,
        "cache_ttl": 1800,
        "cache_max_size": 500,
        "log_level": "INFO",
        "log_format": "text",
        "enable_request_logging": True,
        "enable_metrics": True,
        "metrics_port": 9091,
        "circuit_breaker_threshold": 3,
        "circuit_breaker_timeout": 30
    }


class SampleData:
    """Зразкові дані для тестів API."""

    # Зразки товарів
    PRODUCTS = {
        "simple": {
            "id": 123,
            "sku": "SIMPLE-001",
            "name": "Простий Товар",
            "attribute_set_id": 4,
            "price": 99.99,
            "status": 1,
            "visibility": 4,
            "type_id": "simple",
            "weight": 1.5,
            "created_at": "2023-01-01T10:00:00Z",
            "updated_at": "2023-01-01T10:00:00Z"
        },

        "configurable": {
            "id": 124,
            "sku": "CONF-001",
            "name": "Конфігурований Товар",
            "attribute_set_id": 4,
            "price": 199.99,
            "status": 1,
            "visibility": 4,
            "type_id": "configurable",
            "created_at": "2023-01-01T10:00:00Z",
            "updated_at": "2023-01-01T10:00:00Z"
        },

        "minimal": {
            "sku": "MIN-001",
            "name": "Мінімальний Товар",
            "attribute_set_id": 4,
            "type_id": "simple"
        }
    }

    # Зразки замовлень
    ORDERS = {
        "standard": {
            "entity_id": 456,
            "increment_id": "000000001",
            "status": "processing",
            "state": "processing",
            "customer_email": "customer@example.com",
            "customer_firstname": "Іван",
            "customer_lastname": "Петренко",
            "grand_total": 299.99,
            "subtotal": 299.99,
            "base_currency_code": "UAH",
            "order_currency_code": "UAH",
            "created_at": "2023-01-01T10:00:00Z",
            "items": [
                {
                    "item_id": 1,
                    "sku": "SIMPLE-001",
                    "name": "Простий Товар",
                    "qty_ordered": 3,
                    "price": 99.99,
                    "row_total": 299.97
                }
            ]
        },

        "completed": {
            "entity_id": 457,
            "increment_id": "000000002",
            "status": "complete",
            "state": "complete",
            "customer_email": "completed@example.com",
            "customer_firstname": "Марія",
            "customer_lastname": "Іваненко",
            "grand_total": 150.00,
            "subtotal": 150.00,
            "base_currency_code": "UAH",
            "order_currency_code": "UAH",
            "created_at": "2023-01-02T14:30:00Z"
        }
    }

    # Зразки клієнтів
    CUSTOMERS = {
        "standard": {
            "id": 789,
            "email": "customer@example.com",
            "firstname": "Олександр",
            "lastname": "Коваленко",
            "group_id": 1,
            "store_id": 1,
            "website_id": 1,
            "created_at": "2023-01-01T10:00:00Z",
            "addresses": [
                {
                    "id": 1,
                    "customer_id": 789,
                    "firstname": "Олександр",
                    "lastname": "Коваленко",
                    "street": ["вул. Хрещатик 1"],
                    "city": "Київ",
                    "country_id": "UA",
                    "postcode": "01001",
                    "telephone": "+380501234567",
                    "default_billing": True,
                    "default_shipping": True
                }
            ]
        }
    }


class ErrorResponses:
    """Зразки помилок API для тестування."""

    HTTP_ERRORS = {
        400: {
            "message": "Bad Request",
            "errors": [
                {
                    "field": "sku",
                    "message": "SKU is required"
                }
            ]
        },
        401: {
            "message": "Unauthorized",
            "parameters": {
                "consumer_id": 1,
                "resources": ["Magento_Catalog::products"]
            }
        },
        403: {
            "message": "Forbidden",
            "trace": "Access denied"
        },
        404: {
            "message": "Requested product doesn't exist",
            "parameters": {
                "sku": "NONEXISTENT-SKU"
            }
        },
        422: {
            "message": "Validation Failed",
            "errors": [
                {
                    "field": "product.name",
                    "message": "Product name is required"
                },
                {
                    "field": "product.price",
                    "message": "Price must be positive"
                }
            ]
        },
        429: {
            "message": "Too Many Requests",
            "parameters": {
                "retry_after": 60
            }
        },
        500: {
            "message": "Internal Server Error",
            "trace": "Database connection failed"
        }
    }

    NETWORK_ERRORS = {
        "timeout": "Request timeout after 30 seconds",
        "connection": "Connection refused to test-magento.example.com:443",
        "ssl": "SSL certificate verification failed",
        "dns": "Name resolution failed for test-magento.example.com"
    }


class ValidationTestData:
    """Дані для тестування валідації."""

    INVALID_PRODUCTS = {
        "empty_sku": {
            "sku": "",
            "name": "Товар без SKU",
            "attribute_set_id": 4,
            "type_id": "simple"
        },
        "invalid_price": {
            "sku": "INVALID-PRICE",
            "name": "Товар з поганою ціною",
            "price": -10.99,
            "attribute_set_id": 4,
            "type_id": "simple"
        },
        "missing_required": {
            "name": "Товар без обов'язкових полів"
        }
    }

    INVALID_CUSTOMERS = {
        "invalid_email": {
            "email": "not-an-email",
            "firstname": "Іван",
            "lastname": "Петренко"
        },
        "empty_firstname": {
            "email": "test@example.com",
            "firstname": "",
            "lastname": "Петренко"
        },
        "missing_required": {
            "firstname": "Іван",
            "lastname": "Петренко"
            # відсутній email
        }
    }


class PerformanceConfig:
    """Конфігурація для тестів продуктивності."""

    SMALL_LOAD = {
        "request_count": 10,
        "concurrent_requests": 2,
        "timeout_threshold": 5.0,
        "memory_threshold_mb": 50
    }

    MEDIUM_LOAD = {
        "request_count": 100,
        "concurrent_requests": 10,
        "timeout_threshold": 10.0,
        "memory_threshold_mb": 100
    }

    LARGE_LOAD = {
        "request_count": 1000,
        "concurrent_requests": 50,
        "timeout_threshold": 30.0,
        "memory_threshold_mb": 200
    }


class MockResponses:
    """Заготовлені відповіді для моків."""

    @staticmethod
    def success_response(data, total_count=None):
        """Створити успішну відповідь Magento API."""
        if isinstance(data, list):
            return {
                "items": data,
                "total_count": total_count or len(data)
            }
        return data

    @staticmethod
    def error_response(status_code: int, message: str = None):
        """Створити помилку API."""
        if message is None:
            message = ErrorResponses.HTTP_ERRORS.get(status_code, {}).get("message", "Error")

        return {
            "message": message,
            "status_code": status_code
        }

    @staticmethod
    def paginated_response(items: List[Dict], page: int = 1, page_size: int = 10):
        """Створити пагіновану відповідь."""
        start = (page - 1) * page_size
        end = start + page_size
        page_items = items[start:end]

        return {
            "items": page_items,
            "total_count": len(items),
            "search_criteria": {
                "current_page": page,
                "page_size": page_size
            }
        }


# Експорт для зручності
__all__ = [
    "TestConfig",
    "EnvironmentConfigs",
    "DictConfigs",
    "SampleData",
    "ErrorResponses",
    "ValidationTestData",
    "PerformanceConfig",
    "MockResponses"
]