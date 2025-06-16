"""
Головний клієнт для Magento 2 REST API.

Цей модуль містить основні класи для роботи з Magento API:
- MagentoClient: Асинхронний клієнт з повним функціоналом
- SyncMagentoClient: Синхронна обгортка для простого використання
"""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any, Callable
from contextlib import asynccontextmanager

from .settings import Settings
from .core import DIContainer, BaseClient, HttpAdapter
from .auth import TokenProvider
from .network import RateLimiter
from .exceptions import MagentoError, AuthenticationError

# Імпорт API endpoints (з безпечною обробкою помилок)
try:
    from .endpoints import ProductsEndpoint, OrdersEndpoint
except ImportError:
    # Створюємо заглушки якщо endpoints ще не готові
    class ProductsEndpoint:
        def __init__(self, *args, **kwargs):
            pass

    class OrdersEndpoint:
        def __init__(self, *args, **kwargs):
            pass

import structlog

logger = structlog.get_logger(__name__)


class MagentoClient(BaseClient):
    """
    Головний асинхронний клієнт для Magento 2 REST API.

    Підтримує:
    - Асинхронні операції з async/await
    - Dependency Injection
    - Rate limiting
    - Event-driven архітектуру
    - Кешування
    - Метрики та моніторинг
    """

    def __init__(self, settings: Optional[Settings] = None, **kwargs):
        """
        Ініціалізація клієнта.

        Args:
            settings: Налаштування клієнта
            **kwargs: Додаткові параметри для перевизначення settings
        """
        # Налаштування
        self.settings = settings or Settings.from_env()

        # Перевизначення налаштувань з kwargs
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)

        # Ініціалізація DI контейнера
        self._container = DIContainer()
        self._setup_dependencies()

        # Ініціалізація базового клієнта
        super().__init__(
            settings=self.settings,
            http_adapter=self._container.resolve("HttpAdapter"),
            token_provider=self._container.resolve("TokenProvider")
        )

        # Отримання основних сервісів
        self._rate_limiter = self._container.resolve("RateLimiter")

        # Ініціалізація API endpoints
        self._init_endpoints()

        logger.info("MagentoClient ініціалізовано",
                   base_url=self.settings.base_url,
                   timeout=self.settings.timeout)

    def _setup_dependencies(self):
        """Налаштування Dependency Injection контейнера."""
        # Реєстрація налаштувань
        self._container.register_instance("Settings", self.settings)

        # HTTP адаптер
        self._container.register("HttpAdapter", HttpAdapter)

        # Аутентифікація
        self._container.register("TokenProvider", TokenProvider)

        # Мережеві компоненти
        self._container.register("RateLimiter", RateLimiter)

    def _init_endpoints(self):
        """Ініціалізація API endpoints."""
        try:
            # Створення endpoints
            self.products = ProductsEndpoint(self)
            self.orders = OrdersEndpoint(self)

            logger.debug("API endpoints ініціалізовано")
        except Exception as e:
            logger.warning("Помилка ініціалізації endpoints", error=str(e))
            # Створюємо заглушки
            self.products = ProductsEndpoint(self)
            self.orders = OrdersEndpoint(self)

    @classmethod
    def from_env(cls, env_prefix: str = "MAGENTO") -> "MagentoClient":
        """
        Створення клієнта з змінних оточення.

        Args:
            env_prefix: Префікс для змінних оточення

        Returns:
            Налаштований клієнт
        """
        settings = Settings.from_env_file()
        return cls(settings)

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "MagentoClient":
        """
        Створення клієнта з словника налаштувань.

        Args:
            config: Словник з налаштуваннями

        Returns:
            Налаштований клієнт
        """
        settings = Settings.from_dict(config)
        return cls(settings)

    async def initialize(self):
        """Ініціалізувати клієнт (отримати токени, тощо)."""
        if self._initialized:
            return

        logger.info("Ініціалізація MagentoClient...")

        # Тестуємо з'єднання та отримуємо токен
        try:
            await self.token_provider.get_token()
            self._initialized = True
            logger.info("MagentoClient успішно ініціалізовано")
        except Exception as e:
            logger.error("Помилка ініціалізації клієнта", error=str(e))
            raise AuthenticationError(f"Не вдалося ініціалізувати клієнт: {e}")

    def initialize_sync(self):
        """Sync версія ініціалізації."""
        if self._initialized:
            return

        logger.info("Ініціалізація MagentoClient (синхронно)...")

        try:
            self.token_provider.get_token_sync()
            self._initialized = True
            logger.info("MagentoClient успішно ініціалізовано")
        except Exception as e:
            logger.error("Помилка ініціалізації клієнта", error=str(e))
            raise AuthenticationError(f"Не вдалося ініціалізувати клієнт: {e}")

    # Health check
    async def health_check(self) -> Dict[str, Any]:
        """
        Перевірка здоров'я клієнта та API.

        Returns:
            Словник зі статусом компонентів
        """
        health_status = {
            "client": "healthy",
            "timestamp": time.time(),
            "components": {}
        }

        try:
            # Перевірка API доступності - спробуємо отримати токен
            await self.token_provider.get_token()
            health_status["components"]["api"] = "healthy"
        except Exception as e:
            health_status["components"]["api"] = f"unhealthy: {str(e)}"
            health_status["client"] = "unhealthy"

        # Перевірка Rate Limiter
        try:
            tokens_available = self._rate_limiter.available_tokens()
            health_status["components"]["rate_limiter"] = {
                "status": "healthy",
                "available_tokens": tokens_available
            }
        except Exception as e:
            health_status["components"]["rate_limiter"] = f"unhealthy: {str(e)}"

        return health_status


class SyncMagentoClient:
    """
    Синхронна обгортка над асинхронним MagentoClient.

    Використовується для простого використання без async/await
    у звичайних Python скриптах.
    """

    def __init__(self, settings: Optional[Settings] = None, **kwargs):
        """
        Ініціалізація синхронного клієнта.

        Args:
            settings: Налаштування клієнта
            **kwargs: Додаткові параметри
        """
        self._async_client = MagentoClient(settings, **kwargs)
        self._loop = None
        self._thread = None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="MagentoSync")
        self._closed = False

    def _ensure_loop(self):
        """Забезпечення наявності event loop."""
        if self._loop is None or self._loop.is_closed():
            def run_loop():
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
                self._loop.run_forever()

            self._thread = threading.Thread(target=run_loop, daemon=True)
            self._thread.start()

            # Чекаємо поки loop буде готовий
            while self._loop is None:
                time.sleep(0.01)

    def _run_async(self, coro):
        """Виконання асинхронної операції в синхронному контексті."""
        if self._closed:
            raise MagentoError("Client is closed")

        self._ensure_loop()
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=self._async_client.settings.timeout)

    @classmethod
    def from_env(cls, env_prefix: str = "MAGENTO") -> "SyncMagentoClient":
        """Створення клієнта з змінних оточення."""
        settings = Settings.from_env_file()
        return cls(settings)

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "SyncMagentoClient":
        """Створення клієнта з словника."""
        settings = Settings.from_dict(config)
        return cls(settings)

    # Властивості для доступу до endpoints
    @property
    def products(self):
        """Синхронний доступ до products endpoint."""
        return SyncEndpointWrapper(self._async_client.products, self._run_async)

    @property
    def orders(self):
        """Синхронний доступ до orders endpoint."""
        return SyncEndpointWrapper(self._async_client.orders, self._run_async)

    def health_check(self) -> Dict[str, Any]:
        """Синхронна перевірка здоров'я."""
        return self._run_async(self._async_client.health_check())

    def initialize(self):
        """Ініціалізація синхронного клієнта."""
        self._async_client.initialize_sync()

    def close(self):
        """Закриття синхронного клієнта."""
        if self._closed:
            return

        try:
            # Закриття асинхронного клієнта
            self._run_async(self._async_client.close())
        except Exception as e:
            logger.error("Помилка при закритті async клієнта", error=str(e))

        # Закриття thread pool
        self._executor.shutdown(wait=True)

        # Зупинка event loop
        if self._loop and not self._loop.is_closed():
            self._loop.call_soon_threadsafe(self._loop.stop)
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=5)

        self._closed = True
        logger.info("SyncMagentoClient закрито")

    def __enter__(self):
        """Контекстний менеджер - вхід."""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстний менеджер - вихід."""
        self.close()


class SyncEndpointWrapper:
    """Обгортка для синхронного використання асинхронних endpoints."""

    def __init__(self, async_endpoint, run_async_func):
        self._async_endpoint = async_endpoint
        self._run_async = run_async_func

    def __getattr__(self, name):
        """Проксі всіх методів endpoint."""
        attr = getattr(self._async_endpoint, name)

        if asyncio.iscoroutinefunction(attr):
            # Обгортаємо асинхронні методи
            def sync_wrapper(*args, **kwargs):
                return self._run_async(attr(*args, **kwargs))
            return sync_wrapper
        else:
            # Повертаємо звичайні атрибути як є
            return attr


# Допоміжні функції для швидкого створення клієнтів
def create_client(
    base_url: str,
    username: str,
    password: str,
    **kwargs
) -> MagentoClient:
    """
    Швидке створення асинхронного клієнта.

    Args:
        base_url: URL Magento store
        username: API username
        password: API password
        **kwargs: Додаткові налаштування

    Returns:
        Налаштований MagentoClient
    """
    settings_dict = {
        'base_url': base_url,
        'username': username,
        'password': password,
        **kwargs
    }
    return MagentoClient.from_dict(settings_dict)


def create_sync_client(
    base_url: str,
    username: str,
    password: str,
    **kwargs
) -> SyncMagentoClient:
    """
    Швидке створення синхронного клієнта.

    Args:
        base_url: URL Magento store
        username: API username
        password: API password
        **kwargs: Додаткові налаштування

    Returns:
        Налаштований SyncMagentoClient
    """
    settings_dict = {
        'base_url': base_url,
        'username': username,
        'password': password,
        **kwargs
    }
    return SyncMagentoClient.from_dict(settings_dict)