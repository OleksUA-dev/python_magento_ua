"""HTTP адаптер для роботи з Magento REST API."""

import asyncio
from typing import Any, Dict, Optional, Union
import httpx
from urllib.parse import urljoin

from ..exceptions import (
    NetworkError,
    TimeoutError,
    ConnectionError,
    HTTPError,
    create_http_exception
)


class HttpAdapter:
    """HTTP адаптер з підтримкою async/sync операцій."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        verify_ssl: bool = True,
        proxy: Optional[str] = None,
        max_retries: int = 3,
        **kwargs
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.proxy = proxy
        self.max_retries = max_retries

        # Async клієнт
        self._async_client: Optional[httpx.AsyncClient] = None
        # Sync клієнт
        self._sync_client: Optional[httpx.Client] = None

        # Додаткові параметри для httpx
        self._client_kwargs = {
            'timeout': timeout,
            'verify': verify_ssl,
            'proxies': proxy,
            **kwargs
        }

    @property
    def async_client(self) -> httpx.AsyncClient:
        """Отримати async HTTP клієнт."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(**self._client_kwargs)
        return self._async_client

    @property
    def sync_client(self) -> httpx.Client:
        """Отримати sync HTTP клієнт."""
        if self._sync_client is None:
            self._sync_client = httpx.Client(**self._client_kwargs)
        return self._sync_client

    def _build_url(self, endpoint: str) -> str:
        """Побудувати повний URL для endpoint."""
        return urljoin(self.base_url + '/', endpoint.lstrip('/'))

    def _handle_httpx_error(self, error: Exception) -> None:
        """Конвертувати httpx винятки в наші."""
        if isinstance(error, httpx.TimeoutException):
            raise TimeoutError(f"Request timeout: {error}")
        elif isinstance(error, httpx.ConnectError):
            raise ConnectionError(f"Connection failed: {error}")
        elif isinstance(error, httpx.RequestError):
            raise NetworkError(f"Network error: {error}")
        else:
            raise NetworkError(f"Unexpected error: {error}")

    def _check_response_status(self, response: httpx.Response) -> None:
        """Перевірити статус код відповіді."""
        if not response.is_success:
            try:
                error_data = response.json()
            except:
                error_data = {"message": response.text}

            raise create_http_exception(
                status_code=response.status_code,
                message=error_data.get('message', f'HTTP {response.status_code} error'),
                response_data=error_data,
                endpoint=str(response.url)
            )

    async def request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Виконати async HTTP запит."""
        url = self._build_url(endpoint)

        request_kwargs = {
            'method': method.upper(),
            'url': url,
            'headers': headers or {},
            'params': params,
            'json': json_data,
            'content': data,
            **kwargs
        }

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.async_client.request(**request_kwargs)
                self._check_response_status(response)

                # Повернути JSON якщо можливо, інакше текст
                try:
                    return response.json()
                except:
                    return {"content": response.text}

            except httpx.RequestError as e:
                if attempt == self.max_retries:
                    self._handle_httpx_error(e)
                # Експоненційна затримка між спробами
                await asyncio.sleep(2 ** attempt)
            except HTTPError:
                # HTTP помилки не повторюємо
                raise

    def request_sync(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Виконати sync HTTP запит."""
        url = self._build_url(endpoint)

        request_kwargs = {
            'method': method.upper(),
            'url': url,
            'headers': headers or {},
            'params': params,
            'json': json_data,
            'content': data,
            **kwargs
        }

        for attempt in range(self.max_retries + 1):
            try:
                response = self.sync_client.request(**request_kwargs)
                self._check_response_status(response)

                # Повернути JSON якщо можливо, інакше текст
                try:
                    return response.json()
                except:
                    return {"content": response.text}

            except httpx.RequestError as e:
                if attempt == self.max_retries:
                    self._handle_httpx_error(e)
                # Затримка між спробами
                import time
                time.sleep(2 ** attempt)
            except HTTPError:
                # HTTP помилки не повторюємо
                raise

    # Convenience методи для різних HTTP дій
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET запит."""
        return await self.request('GET', endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """POST запит."""
        return await self.request('POST', endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """PUT запит."""
        return await self.request('PUT', endpoint, **kwargs)

    async def patch(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """PATCH запит."""
        return await self.request('PATCH', endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE запит."""
        return await self.request('DELETE', endpoint, **kwargs)

    # Sync версії
    def get_sync(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Sync GET запит."""
        return self.request_sync('GET', endpoint, **kwargs)

    def post_sync(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Sync POST запит."""
        return self.request_sync('POST', endpoint, **kwargs)

    def put_sync(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Sync PUT запит."""
        return self.request_sync('PUT', endpoint, **kwargs)

    def patch_sync(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Sync PATCH запит."""
        return self.request_sync('PATCH', endpoint, **kwargs)

    def delete_sync(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Sync DELETE запит."""
        return self.request_sync('DELETE', endpoint, **kwargs)

    async def close(self) -> None:
        """Закрити async клієнт."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    def close_sync(self) -> None:
        """Закрити sync клієнт."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None

    async def __aenter__(self):
        """Async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager cleanup."""
        await self.close()

    def __enter__(self):
        """Sync context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager cleanup."""
        self.close_sync()