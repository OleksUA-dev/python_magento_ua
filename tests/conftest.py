"""
Конфігурація pytest та фікстури для тестування.
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

# Додаємо шлях до проекту
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from magento_ua.settings import Settings
from magento_ua.client import MagentoClient
from magento_ua.core.http_adapter import HttpAdapter
from magento_ua.auth.token_provider import TokenProvider


# Фікстури для налаштувань
@pytest.fixture
def test_settings():
    """Налаштування для тестування."""
    return Settings(
        base_url="https://test-magento.example.com",
        username="test_user",
        password="test_password",
        verify_ssl=False,
        timeout=10,
        max_retries=1
    )


@pytest.fixture
def env_settings(monkeypatch):
    """Налаштування через змінні оточення."""
    monkeypatch.setenv("MAGENTO_BASE_URL", "https://env-magento.example.com")
    monkeypatch.setenv("MAGENTO_USERNAME", "env_user")
    monkeypatch.setenv("MAGENTO_PASSWORD", "env_password")
    monkeypatch.setenv("MAGENTO_VERIFY_SSL", "false")

    return Settings.from_env_file()


# Фікстури для моків HTTP
@pytest.fixture
def mock_httpx_response():
    """Мок для httpx Response."""
    mock = Mock()
    mock.status_code = 200
    mock.is_success = True
    mock.json.return_value = {"test": "data"}
    mock.text = "test response"
    mock.url = "https://test.com/api"
    return mock


@pytest.fixture
def mock_httpx_client():
    """Мок для httpx Client."""
    mock = Mock()
    mock.request = Mock()
    mock.close = Mock()
    return mock


@pytest.fixture
def mock_async_httpx_client():
    """Мок для httpx AsyncClient."""
    mock = AsyncMock()
    mock.request = AsyncMock()
    mock.aclose = AsyncMock()
    return mock


# Фікстури для HTTP адаптера
@pytest.fixture
def mock_http_adapter(test_settings):
    """Мок HTTP адаптера."""
    adapter = Mock(spec=HttpAdapter)

    # Async методи
    adapter.request = AsyncMock(return_value={"test": "data"})
    adapter.get = AsyncMock(return_value={"test": "data"})
    adapter.post = AsyncMock(return_value={"test": "data"})
    adapter.put = AsyncMock(return_value={"test": "data"})
    adapter.delete = AsyncMock(return_value={"test": "data"})
    adapter.close = AsyncMock()

    # Sync методи
    adapter.request_sync = Mock(return_value={"test": "data"})
    adapter.get_sync = Mock(return_value={"test": "data"})
    adapter.post_sync = Mock(return_value={"test": "data"})
    adapter.put_sync = Mock(return_value={"test": "data"})
    adapter.delete_sync = Mock(return_value={"test": "data"})
    adapter.close_sync = Mock()

    return adapter


# Фікстури для аутентифікації
@pytest.fixture
def mock_token_provider():
    """Мок провайдера токенів."""
    provider = Mock(spec=TokenProvider)
    provider.get_token = AsyncMock(return_value="test-token-123")
    provider.get_token_sync = Mock(return_value="test-token-123")
    provider.is_authenticated = Mock(return_value=True)
    provider.invalidate_token = AsyncMock()
    provider.invalidate_token_sync = Mock()
    return provider


# Фікстури для клієнта
@pytest.fixture
async def test_client(test_settings, mock_http_adapter, mock_token_provider):
    """Тестовий клієнт з моками."""
    client = MagentoClient(test_settings)

    # Замінюємо залежності на моки
    client.http_adapter = mock_http_adapter
    client.token_provider = mock_token_provider

    yield client

    # Cleanup
    await client.close()


@pytest.fixture
def sync_test_client(test_settings, mock_http_adapter, mock_token_provider):
    """Синхронний тестовий клієнт з моками."""
    from magento_ua.client import SyncMagentoClient

    client = SyncMagentoClient(test_settings)

    # Замінюємо залежності на моки
    client._async_client.http_adapter = mock_http_adapter
    client._async_client.token_provider = mock_token_provider

    yield client

    # Cleanup
    client.close()


# Фікстури для тестових даних
@pytest.fixture
def sample_product_data():
    """Зразок даних товару."""
    return {
        "id": 123,
        "sku": "TEST-PRODUCT-001",
        "name": "Тестовий Товар",
        "attribute_set_id": 4,
        "price": 99.99,
        "status": 1,
        "visibility": 4,
        "type_id": "simple",
        "weight": 1.5,
        "created_at": "2023-01-01T10:00:00Z",
        "updated_at": "2023-01-01T10:00:00Z"
    }


@pytest.fixture
def sample_order_data():
    """Зразок даних замовлення."""
    return {
        "entity_id": 456,
        "increment_id": "000000001",
        "status": "processing",
        "state": "processing",
        "customer_email": "test@example.com",
        "customer_firstname": "Тест",
        "customer_lastname": "Тестовий",
        "grand_total": 199.99,
        "subtotal": 199.99,
        "base_currency_code": "UAH",
        "order_currency_code": "UAH",
        "created_at": "2023-01-01T10:00:00Z",
        "items": [
            {
                "item_id": 1,
                "sku": "TEST-PRODUCT-001",
                "name": "Тестовий Товар",
                "qty_ordered": 2,
                "price": 99.99,
                "row_total": 199.98
            }
        ]
    }


@pytest.fixture
def sample_customer_data():
    """Зразок даних клієнта."""
    return {
        "id": 789,
        "email": "customer@example.com",
        "firstname": "Іван",
        "lastname": "Петренко",
        "group_id": 1,
        "store_id": 1,
        "website_id": 1,
        "created_at": "2023-01-01T10:00:00Z",
        "addresses": [
            {
                "id": 1,
                "customer_id": 789,
                "firstname": "Іван",
                "lastname": "Петренко",
                "street": ["вул. Тестова 123"],
                "city": "Київ",
                "country_id": "UA",
                "postcode": "01001",
                "telephone": "+380501234567",
                "default_billing": True,
                "default_shipping": True
            }
        ]
    }


# Фікстури для помилок
@pytest.fixture
def http_error_responses():
    """Різні типи HTTP помилок."""
    return {
        400: {"message": "Bad Request", "errors": []},
        401: {"message": "Unauthorized"},
        403: {"message": "Forbidden"},
        404: {"message": "Not Found"},
        422: {
            "message": "Validation failed",
            "errors": [{"field": "sku", "message": "SKU required"}]
        },
        429: {"message": "Too Many Requests"},
        500: {"message": "Internal Server Error"}
    }


# Фікстури для мережевих тестів
@pytest.fixture
def network_timeouts():
    """Різні типи таймаутів."""
    import httpx
    return {
        "connect": httpx.ConnectTimeout("Connect timeout"),
        "read": httpx.ReadTimeout("Read timeout"),
        "pool": httpx.PoolTimeout("Pool timeout"),
        "request": httpx.RequestError("Request error")
    }


# Event loop фікстура для async тестів
@pytest.fixture(scope="session")
def event_loop():
    """Створює event loop для сесії."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Фікстури для логування
@pytest.fixture
def capture_logs(caplog):
    """Захоплення логів для перевірки."""
    import logging

    # Налаштовуємо логування
    logging.getLogger("magento_ua").setLevel(logging.DEBUG)

    yield caplog

    # Очищуємо після тесту
    caplog.clear()


# Фікстури для тимчасових файлів
@pytest.fixture
def temp_config_file(tmp_path):
    """Тимчасовий конфігураційний файл."""
    config_file = tmp_path / ".env"
    config_content = """
MAGENTO_BASE_URL=https://temp-test.example.com
MAGENTO_USERNAME=temp_user
MAGENTO_PASSWORD=temp_password
MAGENTO_VERIFY_SSL=false
MAGENTO_TIMEOUT=5
"""
    config_file.write_text(config_content)
    return config_file


# Фікстури для тестування валідації
@pytest.fixture
def invalid_data_samples():
    """Зразки невалідних даних."""
    return {
        "product": {
            "empty_sku": {"sku": "", "name": "Test"},
            "invalid_price": {"sku": "TEST", "price": -10},
            "invalid_status": {"sku": "TEST", "status": 99},
            "missing_required": {"name": "Test"}  # no SKU
        },
        "customer": {
            "invalid_email": {"email": "invalid-email", "firstname": "Test"},
            "empty_firstname": {"email": "test@example.com", "firstname": ""},
            "missing_required": {"firstname": "Test"}  # no email
        }
    }


# Фікстури для тестування performance
@pytest.fixture
def performance_settings():
    """Налаштування для тестування продуктивності."""
    return {
        "request_count": 100,
        "concurrent_requests": 10,
        "timeout_threshold": 5.0,
        "memory_threshold_mb": 100
    }


# Допоміжні функції для тестів
def assert_valid_magento_response(response: Dict[str, Any]):
    """Перевіряє чи є відповідь валідною Magento API відповіддю."""
    assert isinstance(response, dict)
    # Додаткові перевірки можуть бути додані тут


def create_mock_magento_api_response(data: Any, total_count: int = None):
    """Створює мок відповіді Magento API."""
    if isinstance(data, list):
        return {
            "items": data,
            "total_count": total_count or len(data)
        }
    else:
        return data


# Параметризовані фікстури
@pytest.fixture(params=["simple", "configurable", "grouped", "virtual"])
def product_types(request):
    """Параметризована фікстура для різних типів товарів."""
    return request.param


@pytest.fixture(params=[1, 2, 3, 4])
def visibility_options(request):
    """Параметризована фікстура для варіантів видимості."""
    return request.param


@pytest.fixture(params=["pending", "processing", "complete", "canceled"])
def order_statuses(request):
    """Параметризована фікстура для статусів замовлень."""
    return request.param


# Маркери для різних типів тестів
def pytest_configure(config):
    """Конфігурація pytest маркерів."""
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "network: marks tests that require network")
    config.addinivalue_line("markers", "auth: marks tests related to authentication")
    config.addinivalue_line("markers", "validation: marks tests for data validation")
    config.addinivalue_line("markers", "performance: marks performance tests")


# Cleanup для всіх тестів
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Автоматичне очищення після кожного тесту."""
    yield

    # Очищуємо глобальні змінні, кеші, тощо
    # Тут можна додати код для очищення стану між тестами


# Фікстура для моніторингу пам'яті
@pytest.fixture
def memory_monitor():
    """Моніторинг використання пам'яті."""
    import psutil
    import os

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    yield initial_memory

    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_diff = final_memory - initial_memory

    # Попередження якщо пам'ять виросла більше ніж на 50MB
    if memory_diff > 50:
        pytest.warn(f"Memory increased by {memory_diff:.2f}MB during test")