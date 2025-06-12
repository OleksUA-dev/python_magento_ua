"""Провайдер токенів для аутентифікації в Magento API."""

import asyncio
import time
from typing import Optional, TYPE_CHECKING
import httpx

from ..exceptions import AuthenticationError, TokenExpiredError, InvalidTokenError

if TYPE_CHECKING:
    from ..core.http_adapter import HttpAdapter


class TokenProvider:
    """Провайдер для отримання та управління токенами доступу."""

    def __init__(
            self,
            base_url: str,
            username: str,
            password: str,
            http_adapter: Optional['HttpAdapter'] = None,
            token_ttl: int = 14400  # 4 години за замовчуванням
    ):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.token_ttl = token_ttl

        # HTTP адаптер для запитів
        self.http_adapter = http_adapter

        # Кешування токена
        self._token: Optional[str] = None
        self._token_expires_at: Optional[float] = None

        # Блокування для thread-safety
        self._token_lock = asyncio.Lock()
        self._sync_token_lock = False

    async def get_token(self, force_refresh: bool = False) -> str:
        """Отримати валідний токен доступу (async версія)."""
        async with self._token_lock:
            if not force_refresh and self._is_token_valid():
                return self._token

            await self._refresh_token()
            return self._token

    def get_token_sync(self, force_refresh: bool = False) -> str:
        """Отримати валідний токен доступу (sync версія)."""
        # Простий sync lock
        while self._sync_token_lock:
            time.sleep(0.1)

        self._sync_token_lock = True
        try:
            if not force_refresh and self._is_token_valid():
                return self._token

            self._refresh_token_sync()
            return self._token
        finally:
            self._sync_token_lock = False

    def _is_token_valid(self) -> bool:
        """Перевірити, чи токен все ще валідний."""
        if not self._token or not self._token_expires_at:
            return False

        # Додаємо буфер в 60 секунд для безпеки
        return time.time() < (self._token_expires_at - 60)

    async def _refresh_token(self) -> None:
        """Оновити токен через Magento API (async)."""
        if not self.http_adapter:
            raise AuthenticationError("HTTP adapter not configured")

        endpoint = "rest/V1/integration/admin/token"
        payload = {
            "username": self.username,
            "password": self.password
        }

        try:
            response = await self.http_adapter.post(
                endpoint=endpoint,
                json_data=payload
            )

            # Magento повертає токен як простий рядок в лапках
            if isinstance(response, dict) and "content" in response:
                token = response["content"].strip('"')
            elif isinstance(response, str):
                token = response.strip('"')
            else:
                token = str(response).strip('"')

            if not token:
                raise AuthenticationError("Empty token received from Magento API")

            self._token = token
            self._token_expires_at = time.time() + self.token_ttl

        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"Failed to obtain access token: {e}")

    def _refresh_token_sync(self) -> None:
        """Оновити токен через Magento API (sync)."""
        if not self.http_adapter:
            raise AuthenticationError("HTTP adapter not configured")

        endpoint = "rest/V1/integration/admin/token"
        payload = {
            "username": self.username,
            "password": self.password
        }

        try:
            response = self.http_adapter.post_sync(
                endpoint=endpoint,
                json_data=payload
            )

            # Magento повертає токен як простий рядок в лапках
            if isinstance(response, dict) and "content" in response:
                token = response["content"].strip('"')
            elif isinstance(response, str):
                token = response.strip('"')
            else:
                token = str(response).strip('"')

            if not token:
                raise AuthenticationError("Empty token received from Magento API")

            self._token = token
            self._token_expires_at = time.time() + self.token_ttl

        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            raise AuthenticationError(f"Failed to obtain access token: {e}")

    async def invalidate_token(self) -> None:
        """Інвалідувати поточний токен."""
        async with self._token_lock:
            self._token = None
            self._token_expires_at = None

    def invalidate_token_sync(self) -> None:
        """Інвалідувати поточний токен (sync)."""
        while self._sync_token_lock:
            time.sleep(0.1)

        self._sync_token_lock = True
        try:
            self._token = None
            self._token_expires_at = None
        finally:
            self._sync_token_lock = False

    def is_authenticated(self) -> bool:
        """Перевірити, чи є валідний токен."""
        return self._is_token_valid()

    def get_token_info(self) -> dict:
        """Отримати інформацію про поточний токен."""
        return {
            "has_token": self._token is not None,
            "is_valid": self._is_token_valid(),
            "expires_at": self._token_expires_at,
            "expires_in": (
                int(self._token_expires_at - time.time())
                if self._token_expires_at else None
            )
        }

    async def test_connection(self) -> bool:
        """Протестувати з'єднання з Magento API."""
        try:
            token = await self.get_token()
            return bool(token)
        except Exception:
            return False

    def test_connection_sync(self) -> bool:
        """Протестувати з'єднання з Magento API (sync)."""
        try:
            token = self.get_token_sync()
            return bool(token)
        except Exception:
            return False