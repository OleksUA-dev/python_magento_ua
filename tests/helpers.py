"""
Допоміжні функції для тестування.
"""

import os
import contextlib
from typing import Dict, Any, Generator
from unittest.mock import patch

from .config import EnvironmentConfigs, DictConfigs, SampleData, MockResponses


@contextlib.contextmanager
def env_override(env_vars: Dict[str, str]) -> Generator[None, None, None]:
    """
    Контекстний менеджер для тимчасового перевизначення змінних оточення.

    Args:
        env_vars: Словник змінних оточення для встановлення

    Usage:
        with env_override(EnvironmentConfigs.BASIC_ENV):
            # тести з перевизначеними змінними
            pass
    """
    with patch.dict(os.environ, env_vars):
        yield


@contextlib.contextmanager
def clean_env() -> Generator[None, None, None]:
    """
    Контекстний менеджер для очищення всіх MAGENTO_* змінних оточення.
    """
    magento_vars = {k: v for k, v in os.environ.items() if k.startswith("MAGENTO_")}

    # Видаляємо всі MAGENTO_* змінні
    for var in magento_vars:
        if var in os.environ:
            del os.environ[var]

    try:
        yield
    finally:
        # Відновлюємо змінні
        os.environ.update(magento_vars)


def create_test_settings(config_name: str = "minimal"):
    """
    Створити тестові налаштування з предвизначеної конфігурації.

    Args:
        config_name: Назва конфігурації з DictConfigs

    Returns:
        Налаштування для тестів
    """
    from magento_ua.settings import Settings

    config_data = getattr(DictConfigs, config_name.upper(), DictConfigs.MINIMAL)
    return Settings.from_dict(config_data)


def create_mock_response(response_type: str, **kwargs):
    """
    Створити мок відповідь для тестів.

    Args:
        response_type: Тип відповіді (success, error, paginated)
        **kwargs: Додаткові параметри

    Returns:
        Мок відповідь
    """
    if response_type == "success":
        data = kwargs.get("data", SampleData.PRODUCTS["simple"])
        total_count = kwargs.get("total_count")
        return MockResponses.success_response(data, total_count)

    elif response_type == "error":
        status_code = kwargs.get("status_code", 404)
        message = kwargs.get("message")
        return MockResponses.error_response(status_code, message)

    elif response_type == "paginated":
        items = kwargs.get("items", [SampleData.PRODUCTS["simple"]])
        page = kwargs.get("page", 1)
        page_size = kwargs.get("page_size", 10)
        return MockResponses.paginated_response(items, page, page_size)

    else:
        raise ValueError(f"Unknown response type: {response_type}")


def assert_valid_settings(settings):
    """
    Перевірити що налаштування валідні.

    Args:
        settings: Об'єкт Settings для перевірки
    """
    from magento_ua.settings import Settings

    assert isinstance(settings, Settings)
    assert settings.base_url is not None
    assert settings.username
    assert settings.password
    assert settings.timeout > 0
    assert settings.max_retries >= 0


def assert_valid_product(product: Dict[str, Any]):
    """
    Перевірити що дані товару валідні.

    Args:
        product: Словник з даними товару
    """
    required_fields = ["sku", "name"]
    for field in required_fields:
        assert field in product, f"Missing required field: {field}"
        assert product[field], f"Empty required field: {field}"

    if "price" in product:
        assert isinstance(product["price"], (int, float))
        assert product["price"] >= 0

    if "status" in product:
        assert product["status"] in [1, 2]

    if "visibility" in product:
        assert product["visibility"] in [1, 2, 3, 4]


def assert_valid_order(order: Dict[str, Any]):
    """
    Перевірити що дані замовлення валідні.

    Args:
        order: Словник з даними замовлення
    """
    required_fields = ["entity_id", "increment_id", "status"]
    for field in required_fields:
        assert field in order, f"Missing required field: {field}"

    if "grand_total" in order:
        assert isinstance(order["grand_total"], (int, float))
        assert order["grand_total"] >= 0

    if "items" in order:
        assert isinstance(order["items"], list)


def assert_valid_customer(customer: Dict[str, Any]):
    """
    Перевірити що дані клієнта валідні.

    Args:
        customer: Словник з даними клієнта
    """
    required_fields = ["email", "firstname", "lastname"]
    for field in required_fields:
        assert field in customer, f"Missing required field: {field}"
        assert customer[field], f"Empty required field: {field}"

    # Базова перевірка email
    assert "@" in customer["email"]


def create_test_client(config_name: str = "minimal", mock_dependencies: bool = True):
    """
    Створити тестовий клієнт з налаштованими моками.

    Args:
        config_name: Назва конфігурації
        mock_dependencies: Чи замокати залежності

    Returns:
        Тестовий клієнт
    """
    from magento_ua.client import MagentoClient
    from unittest.mock import Mock, AsyncMock

    settings = create_test_settings(config_name)
    client = MagentoClient(settings)

    if mock_dependencies:
        # Мокаємо HTTP адаптер
        client.http_adapter = Mock()
        client.http_adapter.request = AsyncMock(return_value={"test": "data"})
        client.http_adapter.close = AsyncMock()

        # Мокаємо провайдер токенів
        client.token_provider = Mock()
        client.token_provider.get_token = AsyncMock(return_value="test-token-123")
        client.token_provider.is_authenticated = Mock(return_value=True)

    return client


def generate_test_data(data_type: str, count: int = 1, **overrides):
    """
    Згенерувати тестові дані.

    Args:
        data_type: Тип даних (product, order, customer)
        count: Кількість записів
        **overrides: Поля для перевизначення

    Returns:
        Список тестових даних
    """
    if data_type == "product":
        base_data = SampleData.PRODUCTS["simple"].copy()
    elif data_type == "order":
        base_data = SampleData.ORDERS["standard"].copy()
    elif data_type == "customer":
        base_data = SampleData.CUSTOMERS["standard"].copy()
    else:
        raise ValueError(f"Unknown data type: {data_type}")

    results = []
    for i in range(count):
        data = base_data.copy()

        # Додаємо унікальні ідентифікатори
        if data_type == "product":
            data["sku"] = f"TEST-{data_type.upper()}-{i + 1:03d}"
            data["name"] = f"Тестовий {data_type} {i + 1}"
        elif data_type == "order":
            data["entity_id"] = base_data["entity_id"] + i
            data["increment_id"] = f"{int(base_data['increment_id']) + i:09d}"
        elif data_type == "customer":
            data["id"] = base_data["id"] + i
            data["email"] = f"test{i + 1}@example.com"

        # Застосовуємо перевизначення
        data.update(overrides)
        results.append(data)

    return results if count > 1 else results[0]


class TestDataBuilder:
    """Будівельник тестових даних з fluent API."""

    def __init__(self, data_type: str):
        self.data_type = data_type
        self.count = 1
        self.overrides = {}

    def with_count(self, count: int):
        """Встановити кількість записів."""
        self.count = count
        return self

    def with_field(self, field: str, value: Any):
        """Встановити значення поля."""
        self.overrides[field] = value
        return self

    def with_sku(self, sku: str):
        """Встановити SKU (для товарів)."""
        return self.with_field("sku", sku)

    def with_name(self, name: str):
        """Встановити назву."""
        return self.with_field("name", name)

    def with_price(self, price: float):
        """Встановити ціну."""
        return self.with_field("price", price)

    def with_email(self, email: str):
        """Встановити email (для клієнтів)."""
        return self.with_field("email", email)

    def build(self):
        """Побудувати тестові дані."""
        return generate_test_data(self.data_type, self.count, **self.overrides)


def product_builder():
    """Створити будівельник товарів."""
    return TestDataBuilder("product")


def order_builder():
    """Створити будівельник замовлень."""
    return TestDataBuilder("order")


def customer_builder():
    """Створити будівельник клієнтів."""
    return TestDataBuilder("customer")


# Декоратори для тестів
def with_env_config(config_name: str):
    """
    Декоратор для запуску тесту з певною env конфігурацією.

    Args:
        config_name: Назва конфігурації з EnvironmentConfigs
    """

    def decorator(test_func):
        def wrapper(*args, **kwargs):
            env_config = getattr(EnvironmentConfigs, config_name.upper())
            with env_override(env_config):
                return test_func(*args, **kwargs)

        wrapper.__name__ = test_func.__name__
        return wrapper

    return decorator


def requires_real_api(test_func):
    """
    Декоратор для тестів, які потребують реального API.

    Пропускає тест якщо немає змінної MAGENTO_REAL_API_TEST.
    """
    import pytest

    def wrapper(*args, **kwargs):
        if not os.getenv("MAGENTO_REAL_API_TEST"):
            pytest.skip("Real API test skipped (set MAGENTO_REAL_API_TEST=1 to run)")
        return test_func(*args, **kwargs)

    wrapper.__name__ = test_func.__name__
    return wrapper


# Експорт
__all__ = [
    "env_override",
    "clean_env",
    "create_test_settings",
    "create_mock_response",
    "assert_valid_settings",
    "assert_valid_product",
    "assert_valid_order",
    "assert_valid_customer",
    "create_test_client",
    "generate_test_data",
    "TestDataBuilder",
    "product_builder",
    "order_builder",
    "customer_builder",
    "with_env_config",
    "requires_real_api"
]