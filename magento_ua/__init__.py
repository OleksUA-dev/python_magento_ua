"""
Magento Python UA - Сучасний Python клієнт для Magento 2 REST API.

Ця бібліотека надає повнофункціональний інтерфейс для роботи з Magento 2 API
з підтримкою асинхронності, enterprise функцій, безпеки та моніторингу.

Основні можливості:
- Async/await підтримка з можливістю синхронного використання
- Багаторівневі механізми безпеки та шифрування
- Модульна архітектура з dependency injection
- Підтримка брокерів повідомлень (Redis, RabbitMQ)
- Гнучка конфігурація мережі та проксі
- Розумна обробка помилок з Circuit Breaker
- Вбудовані метрики та моніторинг
- Готовність до контейнеризації

Приклад використання:
    >>> import asyncio
    >>> from magento_ua import MagentoClient, Settings
    >>>
    >>> async def main():
    ...     settings = Settings(
    ...         base_url="https://your-store.com",
    ...         username="api_user",
    ...         password="api_password"
    ...     )
    ...
    ...     async with MagentoClient(settings) as client:
    ...         products = await client.products.get_all(limit=10)
    ...         print(f"Знайдено {len(products)} товарів")
    >>>
    >>> asyncio.run(main())

Або синхронно:
    >>> from magento_ua import SyncMagentoClient
    >>>
    >>> with SyncMagentoClient.from_env() as client:
    ...     products = client.products.get_all()
    ...     print(f"Товарів: {len(products)}")
"""

# Версія бібліотеки
__version__ = "1.0.0"
__author__ = "OleksUA-dev"
__email__ = "your-email@example.com"
__license__ = "MIT"

# Основні компоненти для експорту
try:
    from .client import (
        MagentoClient,
        SyncMagentoClient,
        create_client,
        create_sync_client
    )
except ImportError:
    # Поки client.py порожній, створимо заглушки
    MagentoClient = None
    SyncMagentoClient = None
    create_client = None
    create_sync_client = None

from .settings import Settings

# Винятки - експортуємо основні для зручності користувачів
from .exceptions import (
    # Базові винятки
    MagentoError,
    MagentoAPIError,
    MagentoNetworkError,
    MagentoConfigurationError,
    MagentoValidationError,
    MagentoSecurityError,

    # API винятки
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

    # Мережеві винятки
    NetworkError,
    ConnectionError,
    TimeoutError,
    RetryExhaustedError,
    ProxyError,
    SSLError,
)

# Модулі, які мають бути доступні для імпорту
from . import auth
from . import core
from . import network
from . import models
from . import endpoints
from . import utils

# Публічний API - що доступно при from magento_ua import *
__all__ = [
    # Версія
    "__version__",

    # Основні клієнти (додаємо тільки якщо вони існують)
    "Settings",

    # Винятки
    "MagentoError",
    "MagentoAPIError",
    "MagentoNetworkError",
    "MagentoConfigurationError",
    "MagentoValidationError",
    "MagentoSecurityError",
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
    "NetworkError",
    "ConnectionError",
    "TimeoutError",
    "RetryExhaustedError",
    "ProxyError",
    "SSLError",
]

# Додаємо клієнти до експорту якщо вони існують
if MagentoClient is not None:
    __all__.extend([
        "MagentoClient",
        "SyncMagentoClient",
        "create_client",
        "create_sync_client"
    ])

# Налаштування логування за замовчуванням
import logging

# Створюємо logger для бібліотеки
_logger = logging.getLogger(__name__)

# Якщо логування не налаштоване, додаємо NullHandler
if not _logger.handlers:
    _logger.addHandler(logging.NullHandler())

# Функція для швидкого налаштування логування
def setup_logging(level=logging.INFO, format_string=None):
    """
    Швидке налаштування логування для magento_ua.

    Args:
        level: Рівень логування (logging.DEBUG, logging.INFO, тощо)
        format_string: Формат логів (опціонально)
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[logging.StreamHandler()]
    )

    _logger.info(f"Magento UA клієнт v{__version__} - логування налаштовано")

# Додаємо setup_logging до публічного API
__all__.append("setup_logging")

# Перевірка залежностей при імпорті (опціонально)
def _check_dependencies():
    """Перевірка наявності основних залежностей."""
    missing_deps = []

    try:
        import httpx
    except ImportError:
        missing_deps.append("httpx")

    try:
        import pydantic
    except ImportError:
        missing_deps.append("pydantic")

    if missing_deps:
        import warnings
        warnings.warn(
            f"Відсутні залежності: {', '.join(missing_deps)}. "
            f"Встановіть їх: pip install {' '.join(missing_deps)}",
            ImportWarning
        )

# Виконуємо перевірку при імпорті
_check_dependencies()

# Lazy imports для опціональних залежностей
def __getattr__(name):
    """Lazy loading для опціональних компонентів."""

    if name == "RedisCache":
        try:
            from .cache.providers import RedisCache
            return RedisCache
        except ImportError:
            raise ImportError(
                "RedisCache requires redis package. Install with: pip install redis"
            )

    elif name == "RedisBroker":
        try:
            from .events.brokers.redis import RedisBroker
            return RedisBroker
        except ImportError:
            raise ImportError(
                "RedisBroker requires redis package. Install with: pip install redis"
            )

    elif name == "RabbitMQBroker":
        try:
            from .events.brokers.rabbitmq import RabbitMQBroker
            return RabbitMQBroker
        except ImportError:
            raise ImportError(
                "RabbitMQBroker requires aio-pika package. Install with: pip install aio-pika"
            )

    elif name == "PrometheusMetrics":
        try:
            from .metrics.prometheus import MetricsCollector
            return MetricsCollector
        except ImportError:
            raise ImportError(
                "PrometheusMetrics requires prometheus_client. Install with: pip install prometheus_client"
            )

    # Якщо атрибут не знайдено
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Інформація про сумісність
PYTHON_REQUIRES = ">=3.8"
MAGENTO_SUPPORTED_VERSIONS = ["2.3", "2.4"]

# Експорт додаткової інформації
__all__.extend([
    "PYTHON_REQUIRES",
    "MAGENTO_SUPPORTED_VERSIONS"
])

# Функція для отримання інформації про версію
def version_info():
    """
    Повертає детальну інформацію про версію та залежності.

    Returns:
        dict: Словник з інформацією про версію
    """
    import sys
    import platform

    info = {
        "magento_ua_version": __version__,
        "python_version": sys.version,
        "platform": platform.platform(),
        "dependencies": {}
    }

    # Перевіряємо версії залежностей
    dependencies_to_check = [
        "httpx", "pydantic", "cryptography",
        "redis", "aio-pika", "prometheus_client"
    ]

    for dep in dependencies_to_check:
        try:
            module = __import__(dep)
            version = getattr(module, "__version__", "unknown")
            info["dependencies"][dep] = version
        except ImportError:
            info["dependencies"][dep] = "not installed"

    return info

__all__.append("version_info")