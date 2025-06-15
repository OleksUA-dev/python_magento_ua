"""Дата моделі для Magento API."""

from .product import Product, ProductAttribute, ProductImage
from .order import Order, OrderItem, OrderAddress, OrderPayment
from .customer import Customer, CustomerAddress, CustomerGroup
from .category import Category, CategoryProduct

__all__ = [
    'Product', 'ProductAttribute', 'ProductImage',
    'Order', 'OrderItem', 'OrderAddress', 'OrderPayment',
    'Customer', 'CustomerAddress', 'CustomerGroup',
    'Category', 'CategoryProduct'
]