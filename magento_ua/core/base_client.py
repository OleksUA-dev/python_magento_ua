"""Базовий клієнт для Magento API."""

from abc import ABC, abstractmethod
from typing import Dict, Optional, TYPE_CHECKING

from .http_adapter import HttpAdapter
from ..auth.token_provider import TokenProvider
from ..settings import Settings
from ..exceptions import AuthenticationError

if TYPE_CHECKING:
    pass


class BaseClient(ABC):
    """Абстрактний базовий клієнт для Magento API."""

    def __init__(
            self,
            settings: Settings,
            http_adapter: Optional[HttpAdapter] = None,
            token_provider: Optional[TokenProvider] = None
    ):
        self.settings = settings

        # HTTP адаптер
        self.http_adapter = http_adapter or HttpAdapter(
            base_url=settings.base_url,
            timeout=settings.timeout,
            verify_ssl=settings.verify_ssl,
            proxy=settings.proxy_url,
            max_retries=settings.max_retries
        )

        # Провайдер токенів
        self.token_provider = token_provider or TokenProvider(
            base_url=settings.base_url,
            username=settings.username,
            password=settings.password,
            http_adapter=self.http_adapter
        )

        # Стан ініціалізації
        self._initialized = False

    @abstractmethod
    async def initialize(self) -> None:
        """Ініціалізувати клієнт (отримати токени, тощо)."""
        pass

    @abstractmethod
    def initialize_sync(self) -> None:
        """Sync версія ініціалізації."""
        pass

    async def get_auth_headers(self) -> Dict[str, str]:
        """Отримати заголовки авторизації для async запитів."""
        if not self._initialized:
            await self.initialize()

        token = await self.token_provider.get_token()
        if not token:
            raise AuthenticationError("Failed to obtain access token")

        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get_auth_headers_sync(self) -> Dict[str, str]:
        """Отримати заголовки авторизації для sync запитів."""
        if not self._initialized:
            self.initialize_sync()

        token = self.token_provider.get_token_sync()
        if not token:
            raise AuthenticationError("Failed to obtain access token")

        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def close(self) -> None:
        """Закрити клієнт та звільнити ресурси."""
        await self.http_adapter.close()
        self._initialized = False

    def close_sync(self) -> None:
        """Sync версія закриття клієнта."""
        self.http_adapter.close_sync()
        self._initialized = False

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def __enter__(self):
        """Sync context manager entry."""
        self.initialize_sync()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit."""
        self.close_sync()