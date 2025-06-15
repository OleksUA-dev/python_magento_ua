"""Модель замовлення Magento."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


class OrderStatus(Enum):
    """Статуси замовлення."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    CANCELED = "canceled"
    CLOSED = "closed"
    FRAUD = "fraud"
    HOLDED = "holded"
    PAYMENT_REVIEW = "payment_review"


@dataclass
class OrderAddress:
    """Адреса в замовленні."""
    address_type: str  # billing or shipping
    city: str = ""
    country_id: str = ""
    email: Optional[str] = None
    firstname: str = ""
    lastname: str = ""
    postcode: str = ""
    region: Optional[str] = None
    region_id: Optional[int] = None
    street: List[str] = field(default_factory=list)
    telephone: Optional[str] = None
    company: Optional[str] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'OrderAddress':
        """Створити з API відповіді."""
        return cls(
            address_type=data.get('address_type', ''),
            city=data.get('city', ''),
            country_id=data.get('country_id', ''),
            email=data.get('email'),
            firstname=data.get('firstname', ''),
            lastname=data.get('lastname', ''),
            postcode=data.get('postcode', ''),
            region=data.get('region'),
            region_id=data.get('region_id'),
            street=data.get('street', []),
            telephone=data.get('telephone'),
            company=data.get('company')
        )


@dataclass
class OrderPayment:
    """Платіж замовлення."""
    method: str = ""
    amount_ordered: Decimal = field(default_factory=lambda: Decimal('0'))
    amount_paid: Decimal = field(default_factory=lambda: Decimal('0'))
    cc_last4: Optional[str] = None
    additional_information: List[str] = field(default_factory=list)

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'OrderPayment':
        """Створити з API відповіді."""
        return cls(
            method=data.get('method', ''),
            amount_ordered=Decimal(str(data.get('amount_ordered', 0))),
            amount_paid=Decimal(str(data.get('amount_paid', 0))),
            cc_last4=data.get('cc_last4'),
            additional_information=data.get('additional_information', [])
        )


@dataclass
class OrderItem:
    """Товар в замовленні."""
    item_id: Optional[int] = None
    sku: str = ""
    name: str = ""
    product_id: Optional[int] = None
    qty_ordered: Decimal = field(default_factory=lambda: Decimal('0'))
    price: Decimal = field(default_factory=lambda: Decimal('0'))
    row_total: Decimal = field(default_factory=lambda: Decimal('0'))
    product_type: str = "simple"

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'OrderItem':
        """Створити з API відповіді."""
        return cls(
            item_id=data.get('item_id'),
            sku=data.get('sku', ''),
            name=data.get('name', ''),
            product_id=data.get('product_id'),
            qty_ordered=Decimal(str(data.get('qty_ordered', 0))),
            price=Decimal(str(data.get('price', 0))),
            row_total=Decimal(str(data.get('row_total', 0))),
            product_type=data.get('product_type', 'simple')
        )


@dataclass
class Order:
    """Модель замовлення Magento."""

    # Основні властивості
    entity_id: Optional[int] = None
    increment_id: Optional[str] = None
    status: str = OrderStatus.PENDING.value
    state: str = "new"

    # Клієнт
    customer_id: Optional[int] = None
    customer_email: str = ""
    customer_firstname: str = ""
    customer_lastname: str = ""
    customer_is_guest: bool = False

    # Фінанси
    base_currency_code: str = "USD"
    order_currency_code: str = "USD"
    base_grand_total: Decimal = field(default_factory=lambda: Decimal('0'))
    grand_total: Decimal = field(default_factory=lambda: Decimal('0'))
    base_subtotal: Decimal = field(default_factory=lambda: Decimal('0'))
    subtotal: Decimal = field(default_factory=lambda: Decimal('0'))
    base_tax_amount: Decimal = field(default_factory=lambda: Decimal('0'))
    tax_amount: Decimal = field(default_factory=lambda: Decimal('0'))
    base_shipping_amount: Decimal = field(default_factory=lambda: Decimal('0'))
    shipping_amount: Decimal = field(default_factory=lambda: Decimal('0'))
    base_discount_amount: Decimal = field(default_factory=lambda: Decimal('0'))
    discount_amount: Decimal = field(default_factory=lambda: Decimal('0'))

    # Дати
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Колекції
    items: List[OrderItem] = field(default_factory=list)
    billing_address: Optional[OrderAddress] = None
    shipping_address: Optional[OrderAddress] = None
    payment: Optional[OrderPayment] = None

    # Доставка
    shipping_method: Optional[str] = None
    shipping_description: Optional[str] = None

    # Сирі дані
    _raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'Order':
        """Створити замовлення з API відповіді."""
        order = cls()

        # Основні поля
        order.entity_id = data.get('entity_id')
        order.increment_id = data.get('increment_id')
        order.status = data.get('status', OrderStatus.PENDING.value)
        order.state = data.get('state', 'new')

        # Клієнт
        order.customer_id = data.get('customer_id')
        order.customer_email = data.get('customer_email', '')
        order.customer_firstname = data.get('customer_firstname', '')
        order.customer_lastname = data.get('customer_lastname', '')
        order.customer_is_guest = bool(data.get('customer_is_guest', False))

        # Валюта
        order.base_currency_code = data.get('base_currency_code', 'USD')
        order.order_currency_code = data.get('order_currency_code', 'USD')

        # Фінанси
        financial_fields = [
            'base_grand_total', 'grand_total', 'base_subtotal', 'subtotal',
            'base_tax_amount', 'tax_amount', 'base_shipping_amount', 'shipping_amount',
            'base_discount_amount', 'discount_amount'
        ]

        for field_name in financial_fields:
            if field_name in data:
                setattr(order, field_name, Decimal(str(data[field_name])))

        # Дати
        if 'created_at' in data:
            order.created_at = datetime.fromisoformat(
                data['created_at'].replace('Z', '+00:00')
            )
        if 'updated_at' in data:
            order.updated_at = datetime.fromisoformat(
                data['updated_at'].replace('Z', '+00:00')
            )

        # Товари
        if 'items' in data:
            order.items = [OrderItem.from_api(item) for item in data['items']]

        # Адреси
        if 'billing_address' in data:
            order.billing_address = OrderAddress.from_api(data['billing_address'])
        if 'extension_attributes' in data and 'shipping_assignments' in data['extension_attributes']:
            shipping_assignments = data['extension_attributes']['shipping_assignments']
            if shipping_assignments and 'shipping' in shipping_assignments[0]:
                shipping_info = shipping_assignments[0]['shipping']
                if 'address' in shipping_info:
                    order.shipping_address = OrderAddress.from_api(shipping_info['address'])
                if 'method' in shipping_info:
                    order.shipping_method = shipping_info['method']

        # Платіж
        if 'payment' in data:
            order.payment = OrderPayment.from_api(data['payment'])

        # Доставка
        order.shipping_method = data.get('shipping_method')
        order.shipping_description = data.get('shipping_description')

        # Сирі дані
        order._raw_data = data

        return order

    def get_total_qty(self) -> Decimal:
        """Отримати загальну кількість товарів."""
        return sum(item.qty_ordered for item in self.items)

    def get_items_by_sku(self, sku: str) -> List[OrderItem]:
        """Отримати товари за SKU."""
        return [item for item in self.items if item.sku == sku]

    def __str__(self) -> str:
        return f"Order(#{self.increment_id}, status='{self.status}', total={self.grand_total})"