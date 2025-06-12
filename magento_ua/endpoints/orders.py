# magento_ua/endpoints/orders.py
"""Endpoint для роботи з замовленнями."""

from typing import Dict, Any, Optional, List
import structlog

from .base import BaseEndpoint
from ..exceptions import NotFoundError, ValidationError

logger = structlog.get_logger(__name__)


class OrdersEndpoint(BaseEndpoint):
    """Endpoint для роботи з замовленнями Magento."""

    async def get_all(
            self,
            limit: Optional[int] = None,
            page: Optional[int] = None,
            filters: Optional[Dict[str, Any]] = None,
            sort_orders: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Отримати список всіх замовлень.

        Args:
            limit: Ліміт замовлень на сторінку
            page: Номер сторінки
            filters: Фільтри для пошуку
            sort_orders: Порядок сортування

        Returns:
            Список замовлень
        """
        params = self._build_search_criteria(
            filters=filters,
            sort_orders=sort_orders,
            page_size=limit,
            current_page=page
        )

        logger.info("Отримання списку замовлень", params=params)

        response = await self._request("GET", "orders", params=params)
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

        logger.info("Отримання списку замовлень (синхронно)", params=params)

        response = self._request_sync("GET", "orders", params=params)
        return self._extract_items(response)

    async def get_by_id(self, order_id: int) -> Dict[str, Any]:
        """
        Отримати замовлення за ID.

        Args:
            order_id: ID замовлення

        Returns:
            Дані замовлення

        Raises:
            NotFoundError: Якщо замовлення не знайдено
        """
        if not order_id or order_id <= 0:
            raise ValidationError("ID замовлення має бути позитивним числом")

        logger.info("Отримання замовлення за ID", order_id=order_id)

        try:
            response = await self._request("GET", f"orders/{order_id}")
            return response
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise NotFoundError(f"Замовлення з ID {order_id} не знайдено")
            raise

    def get_by_id_sync(self, order_id: int) -> Dict[str, Any]:
        """Синхронна версія get_by_id."""
        if not order_id or order_id <= 0:
            raise ValidationError("ID замовлення має бути позитивним числом")

        logger.info("Отримання замовлення за ID (синхронно)", order_id=order_id)

        try:
            response = self._request_sync("GET", f"orders/{order_id}")
            return response
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise NotFoundError(f"Замовлення з ID {order_id} не знайдено")
            raise

    async def get_by_increment_id(self, increment_id: str) -> Dict[str, Any]:
        """
        Отримати замовлення за increment ID (номер замовлення).

        Args:
            increment_id: Номер замовлення

        Returns:
            Дані замовлення
        """
        if not increment_id:
            raise ValidationError("Номер замовлення не може бути порожнім")

        filters = {
            "increment_id": increment_id
        }

        orders = await self.get_all(limit=1, filters=filters)

        if not orders:
            raise NotFoundError(f"Замовлення з номером {increment_id} не знайдено")

        return orders[0]

    def get_by_increment_id_sync(self, increment_id: str) -> Dict[str, Any]:
        """Синхронна версія get_by_increment_id."""
        if not increment_id:
            raise ValidationError("Номер замовлення не може бути порожнім")

        filters = {
            "increment_id": increment_id
        }

        orders = self.get_all_sync(limit=1, filters=filters)

        if not orders:
            raise NotFoundError(f"Замовлення з номером {increment_id} не знайдено")

        return orders[0]

    async def get_by_status(
            self,
            status: str,
            limit: Optional[int] = None,
            page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Отримати замовлення за статусом.

        Args:
            status: Статус замовлення
            limit: Ліміт замовлень
            page: Номер сторінки

        Returns:
            Список замовлень з вказаним статусом
        """
        if not status:
            raise ValidationError("Статус не може бути порожнім")

        filters = {
            "status": status
        }

        return await self.get_all(
            limit=limit,
            page=page,
            filters=filters
        )

    def get_by_status_sync(
            self,
            status: str,
            limit: Optional[int] = None,
            page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Синхронна версія get_by_status."""
        if not status:
            raise ValidationError("Статус не може бути порожнім")

        filters = {
            "status": status
        }

        return self.get_all_sync(
            limit=limit,
            page=page,
            filters=filters
        )

    async def update_status(
            self,
            order_id: int,
            status: str,
            comment: Optional[str] = None,
            notify_customer: bool = False
    ) -> bool:
        """
        Оновити статус замовлення.

        Args:
            order_id: ID замовлення
            status: Новий статус
            comment: Коментар до зміни статусу
            notify_customer: Сповістити клієнта про зміну

        Returns:
            True якщо статус оновлено успішно
        """
        if not order_id or order_id <= 0:
            raise ValidationError("ID замовлення має бути позитивним числом")

        if not status:
            raise ValidationError("Статус не може бути порожнім")

        payload = {
            "status": status,
            "comment": comment or "",
            "isCustomerNotified": notify_customer
        }

        logger.info("Оновлення статусу замовлення",
                    order_id=order_id, status=status)

        response = await self._request(
            "POST",
            f"orders/{order_id}/comments",
            data=payload
        )

        return bool(response)

    def update_status_sync(
            self,
            order_id: int,
            status: str,
            comment: Optional[str] = None,
            notify_customer: bool = False
    ) -> bool:
        """Синхронна версія update_status."""
        if not order_id or order_id <= 0:
            raise ValidationError("ID замовлення має бути позитивним числом")

        if not status:
            raise ValidationError("Статус не може бути порожнім")

        payload = {
            "status": status,
            "comment": comment or "",
            "isCustomerNotified": notify_customer
        }

        logger.info("Оновлення статусу замовлення (синхронно)",
                    order_id=order_id, status=status)

        response = self._request_sync(
            "POST",
            f"orders/{order_id}/comments",
            data=payload
        )

        return bool(response)