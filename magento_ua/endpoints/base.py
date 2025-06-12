"""Базовий клас для всіх API endpoints."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from urllib.parse import urljoin

from ..exceptions import APIError, ValidationError

if TYPE_CHECKING:
    from ..core.base_client import BaseClient


class BaseEndpoint(ABC):
    """Абстрактний базовий клас для всіх endpoints."""

    def __init__(self, client: 'BaseClient'):
        self._client = client

    @property
    @abstractmethod
    def endpoint_path(self) -> str:
        """Базовий шлях для endpoint (наприклад, 'products')."""
        pass

    def _build_endpoint(self, path: str = "") -> str:
        """Побудувати повний шлях до endpoint."""
        base = f"rest/V1/{self.endpoint_path.strip('/')}"
        if path:
            return f"{base}/{path.strip('/')}"
        return base

    def _build_search_criteria(
            self,
            filters: Optional[Dict[str, Any]] = None,
            sort_orders: Optional[List[Dict[str, str]]] = None,
            page_size: Optional[int] = None,
            current_page: Optional[int] = None
    ) -> Dict[str, Any]:
        """Побудувати Magento search criteria."""
        search_criteria = {}

        # Фільтри
        if filters:
            filter_groups = []
            for field, value in filters.items():
                if isinstance(value, dict):
                    # Складний фільтр з умовою
                    condition = value.get('condition', 'eq')
                    filter_value = value.get('value')
                else:
                    # Простий фільтр
                    condition = 'eq'
                    filter_value = value

                filter_groups.append({
                    "filters": [{
                        "field": field,
                        "value": filter_value,
                        "condition_type": condition
                    }]
                })

            search_criteria["filterGroups"] = filter_groups

        # Сортування
        if sort_orders:
            search_criteria["sortOrders"] = sort_orders

        # Пагінація
        if page_size is not None:
            search_criteria["pageSize"] = page_size

        if current_page is not None:
            search_criteria["currentPage"] = current_page

        return {"searchCriteria": search_criteria}

    def _extract_items(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Витягти items з Magento відповіді."""
        if "items" in response:
            return response["items"]
        elif isinstance(response, list):
            return response
        elif isinstance(response, dict) and "id" in response:
            # Одиночний об'єкт
            return [response]
        else:
            raise APIError(f"Unexpected response format: {response}")

    def _extract_total_count(self, response: Dict[str, Any]) -> int:
        """Витягти total_count з Magento відповіді."""
        return response.get("total_count", len(self._extract_items(response)))

    def _validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """Перевірити обов'язкові поля."""
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

    async def _request(
            self,
            method: str,
            endpoint: str = "",
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Any]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Виконати async запит до API."""
        full_endpoint = self._build_endpoint(endpoint)

        # Додати авторизацію
        auth_headers = await self._client.get_auth_headers()
        if headers:
            headers.update(auth_headers)
        else:
            headers = auth_headers

        return await self._client.http_adapter.request(
            method=method,
            endpoint=full_endpoint,
            headers=headers,
            params=params,
            json_data=json_data,
            **kwargs
        )

    def _request_sync(
            self,
            method: str,
            endpoint: str = "",
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Any]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """Виконати sync запит до API."""
        full_endpoint = self._build_endpoint(endpoint)

        # Додати авторизацію
        auth_headers = self._client.get_auth_headers_sync()
        if headers:
            headers.update(auth_headers)
        else:
            headers = auth_headers

        return self._client.http_adapter.request_sync(
            method=method,
            endpoint=full_endpoint,
            headers=headers,
            params=params,
            json_data=json_data,
            **kwargs
        )

    # Стандартні CRUD операції (можуть бути перевизначені в дочірніх класах)

    async def get_all(
            self,
            filters: Optional[Dict[str, Any]] = None,
            sort_orders: Optional[List[Dict[str, str]]] = None,
            limit: Optional[int] = None,
            page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Отримати всі записи з фільтрацією."""
        params = self._build_search_criteria(
            filters=filters,
            sort_orders=sort_orders,
            page_size=limit,
            current_page=page
        )

        response = await self._request("GET", params=params)
        return self._extract_items(response)

    def get_all_sync(
            self,
            filters: Optional[Dict[str, Any]] = None,
            sort_orders: Optional[List[Dict[str, str]]] = None,
            limit: Optional[int] = None,
            page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Sync версія get_all."""
        params = self._build_search_criteria(
            filters=filters,
            sort_orders=sort_orders,
            page_size=limit,
            current_page=page
        )

        response = self._request_sync("GET", params=params)
        return self._extract_items(response)

    async def get_by_id(self, entity_id: Union[int, str]) -> Dict[str, Any]:
        """Отримати запис за ID."""
        response = await self._request("GET", endpoint=str(entity_id))
        if isinstance(response, dict):
            return response
        else:
            raise APIError(f"Unexpected response format for ID {entity_id}")

    def get_by_id_sync(self, entity_id: Union[int, str]) -> Dict[str, Any]:
        """Sync версія get_by_id."""
        response = self._request_sync("GET", endpoint=str(entity_id))
        if isinstance(response, dict):
            return response
        else:
            raise APIError(f"Unexpected response format for ID {entity_id}")

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Створити новий запис."""
        # Обгорнути дані в структуру, специфічну для endpoint
        wrapped_data = self._wrap_entity_data(data)
        response = await self._request("POST", json_data=wrapped_data)
        return response

    def create_sync(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync версія create."""
        wrapped_data = self._wrap_entity_data(data)
        response = self._request_sync("POST", json_data=wrapped_data)
        return response

    async def update(self, entity_id: Union[int, str], data: Dict[str, Any]) -> Dict[str, Any]:
        """Оновити існуючий запис."""
        wrapped_data = self._wrap_entity_data(data)
        response = await self._request("PUT", endpoint=str(entity_id), json_data=wrapped_data)
        return response

    def update_sync(self, entity_id: Union[int, str], data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync версія update."""
        wrapped_data = self._wrap_entity_data(data)
        response = self._request_sync("PUT", endpoint=str(entity_id), json_data=wrapped_data)
        return response

    async def delete(self, entity_id: Union[int, str]) -> bool:
        """Видалити запис за ID."""
        try:
            await self._request("DELETE", endpoint=str(entity_id))
            return True
        except Exception:
            return False

    def delete_sync(self, entity_id: Union[int, str]) -> bool:
        """Sync версія delete."""
        try:
            self._request_sync("DELETE", endpoint=str(entity_id))
            return True
        except Exception:
            return False

    def _wrap_entity_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обгорнути дані в Magento структуру.

        Має бути перевизначено в дочірніх класах.
        Наприклад, для products: {"product": data}
        """
        return data