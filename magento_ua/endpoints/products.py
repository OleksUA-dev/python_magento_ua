# magento_ua/endpoints/products.py
"""Endpoint для роботи з товарами."""

from typing import Dict, Any, Optional, List, Union
import structlog

from .base import BaseEndpoint
from ..exceptions import NotFoundError, ValidationError

logger = structlog.get_logger(__name__)


class ProductsEndpoint(BaseEndpoint):
    """Endpoint для роботи з товарами Magento."""

    async def get_all(
            self,
            limit: Optional[int] = None,
            page: Optional[int] = None,
            filters: Optional[Dict[str, Any]] = None,
            sort_orders: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Отримати список всіх товарів.

        Args:
            limit: Ліміт товарів на сторінку
            page: Номер сторінки (починаючи з 1)
            filters: Фільтри для пошуку
            sort_orders: Порядок сортування

        Returns:
            Список товарів
        """
        params = self._build_search_criteria(
            filters=filters,
            sort_orders=sort_orders,
            page_size=limit,
            current_page=page
        )

        logger.info("Отримання списку товарів", params=params)

        response = await self._request("GET", "products", params=params)
        return self._extract_items(response)

    def get_all_sync(
            self,
            limit: Optional[int] = None,
            page: Optional[int] = None,
            filters: Optional[Dict[str, Any]] = None,
            sort_orders: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, Any]]:
        """Синхронна версія get_all."""
        params = self._build_search_criteria(
            filters=filters,
            sort_orders=sort_orders,
            page_size=limit,
            current_page=page
        )

        logger.info("Отримання списку товарів (синхронно)", params=params)

        response = self._request_sync("GET", "products", params=params)
        return self._extract_items(response)

    async def get_by_sku(self, sku: str) -> Dict[str, Any]:
        """
        Отримати товар за SKU.

        Args:
            sku: SKU товару

        Returns:
            Дані товару

        Raises:
            NotFoundError: Якщо товар не знайдено
        """
        if not sku:
            raise ValidationError("SKU не може бути порожнім")

        logger.info("Отримання товару за SKU", sku=sku)

        try:
            response = await self._request("GET", f"products/{sku}")
            return response
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise NotFoundError(f"Товар з SKU '{sku}' не знайдено")
            raise

    def get_by_sku_sync(self, sku: str) -> Dict[str, Any]:
        """Синхронна версія get_by_sku."""
        if not sku:
            raise ValidationError("SKU не може бути порожнім")

        logger.info("Отримання товару за SKU (синхронно)", sku=sku)

        try:
            response = self._request_sync("GET", f"products/{sku}")
            return response
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise NotFoundError(f"Товар з SKU '{sku}' не знайдено")
            raise

    async def create(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Створити новий товар.

        Args:
            product_data: Дані товару

        Returns:
            Створений товар

        Raises:
            ValidationError: Якщо дані товару невалідні
        """
        if not product_data:
            raise ValidationError("Дані товару не можуть бути порожніми")

        if "sku" not in product_data:
            raise ValidationError("SKU обов'язковий для створення товару")

        # Обгорнути в структуру product
        payload = {"product": product_data}

        logger.info("Створення товару", sku=product_data.get("sku"))

        response = await self._request("POST", "products", data=payload)
        return response

    def create_sync(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Синхронна версія create."""
        if not product_data:
            raise ValidationError("Дані товару не можуть бути порожніми")

        if "sku" not in product_data:
            raise ValidationError("SKU обов'язковий для створення товару")

        payload = {"product": product_data}

        logger.info("Створення товару (синхронно)", sku=product_data.get("sku"))

        response = self._request_sync("POST", "products", data=payload)
        return response

    async def update(self, sku: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Оновити товар.

        Args:
            sku: SKU товару для оновлення
            product_data: Нові дані товару

        Returns:
            Оновлений товар
        """
        if not sku:
            raise ValidationError("SKU не може бути порожнім")

        if not product_data:
            raise ValidationError("Дані товару не можуть бути порожніми")

        # Обгорнути в структуру product
        payload = {"product": product_data}

        logger.info("Оновлення товару", sku=sku)

        response = await self._request("PUT", f"products/{sku}", data=payload)
        return response

    def update_sync(self, sku: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Синхронна версія update."""
        if not sku:
            raise ValidationError("SKU не може бути порожнім")

        if not product_data:
            raise ValidationError("Дані товару не можуть бути порожніми")

        payload = {"product": product_data}

        logger.info("Оновлення товару (синхронно)", sku=sku)

        response = self._request_sync("PUT", f"products/{sku}", data=payload)
        return response

    async def delete(self, sku: str) -> bool:
        """
        Видалити товар.

        Args:
            sku: SKU товару для видалення

        Returns:
            True якщо товар видалено успішно
        """
        if not sku:
            raise ValidationError("SKU не може бути порожнім")

        logger.info("Видалення товару", sku=sku)

        response = await self._request("DELETE", f"products/{sku}")

        # Magento повертає true/false для операцій видалення
        return bool(response)

    def delete_sync(self, sku: str) -> bool:
        """Синхронна версія delete."""
        if not sku:
            raise ValidationError("SKU не може бути порожнім")

        logger.info("Видалення товару (синхронно)", sku=sku)

        response = self._request_sync("DELETE", f"products/{sku}")

        return bool(response)

    async def search(
            self,
            query: str,
            limit: Optional[int] = None,
            page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Пошук товарів за текстовим запитом.

        Args:
            query: Пошуковий запит
            limit: Ліміт результатів
            page: Номер сторінки

        Returns:
            Список знайдених товарів
        """
        if not query:
            raise ValidationError("Пошуковий запит не може бути порожнім")

        # Пошук за назвою товару
        filters = {
            "name": {
                "condition": "like",
                "value": f"%{query}%"
            }
        }

        return await self.get_all(
            limit=limit,
            page=page,
            filters=filters
        )

    def search_sync(
            self,
            query: str,
            limit: Optional[int] = None,
            page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Синхронна версія search."""
        if not query:
            raise ValidationError("Пошуковий запит не може бути порожнім")

        filters = {
            "name": {
                "condition": "like",
                "value": f"%{query}%"
            }
        }

        return self.get_all_sync(
            limit=limit,
            page=page,
            filters=filters
        )

    async def get_by_category(
            self,
            category_id: int,
            limit: Optional[int] = None,
            page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Отримати товари за категорією.

        Args:
            category_id: ID категорії
            limit: Ліміт товарів
            page: Номер сторінки

        Returns:
            Список товарів з категорії
        """
        filters = {
            "category_id": category_id
        }

        return await self.get_all(
            limit=limit,
            page=page,
            filters=filters
        )

    def get_by_category_sync(
            self,
            category_id: int,
            limit: Optional[int] = None,
            page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Синхронна версія get_by_category."""
        filters = {
            "category_id": category_id
        }

        return self.get_all_sync(
            limit=limit,
            page=page,
            filters=filters
        )