"""Експорт всіх API endpoints."""

from .base import BaseEndpoint

# Імпорт endpoints - додаються поступово
try:
    from .products import ProductsEndpoint
except ImportError:
    ProductsEndpoint = None

try:
    from .orders import OrdersEndpoint
except ImportError:
    OrdersEndpoint = None

__all__ = [
    "BaseEndpoint",
]

# Додаємо до експорту тільки доступні endpoints
if ProductsEndpoint:
    __all__.append("ProductsEndpoint")

if OrdersEndpoint:
    __all__.append("OrdersEndpoint")