"""Модель клієнта Magento."""

from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class Gender(Enum):
    """Стать клієнта."""
    MALE = 1
    FEMALE = 2
    NOT_SPECIFIED = 3


@dataclass
class CustomerAddress:
    """Адреса клієнта."""
    id: Optional[int] = None
    customer_id: Optional[int] = None
    region: Optional[str] = None
    region_id: Optional[int] = None
    country_id: str = ""
    street: List[str] = field(default_factory=list)
    company: Optional[str] = None
    telephone: Optional[str] = None
    fax: Optional[str] = None
    postcode: str = ""
    city: str = ""
    firstname: str = ""
    lastname: str = ""
    middlename: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    vat_id: Optional[str] = None
    default_shipping: bool = False
    default_billing: bool = False

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'CustomerAddress':
        """Створити з API відповіді."""
        return cls(
            id=data.get('id'),
            customer_id=data.get('customer_id'),
            region=data.get('region'),
            region_id=data.get('region_id'),
            country_id=data.get('country_id', ''),
            street=data.get('street', []),
            company=data.get('company'),
            telephone=data.get('telephone'),
            fax=data.get('fax'),
            postcode=data.get('postcode', ''),
            city=data.get('city', ''),
            firstname=data.get('firstname', ''),
            lastname=data.get('lastname', ''),
            middlename=data.get('middlename'),
            prefix=data.get('prefix'),
            suffix=data.get('suffix'),
            vat_id=data.get('vat_id'),
            default_shipping=data.get('default_shipping', False),
            default_billing=data.get('default_billing', False)
        )

    def to_api(self) -> Dict[str, Any]:
        """Конвертувати в API формат."""
        data = {
            'region': self.region,
            'region_id': self.region_id,
            'country_id': self.country_id,
            'street': self.street,
            'postcode': self.postcode,
            'city': self.city,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'default_shipping': self.default_shipping,
            'default_billing': self.default_billing
        }

        # Додаткові поля
        optional_fields = ['company', 'telephone', 'fax', 'middlename', 'prefix', 'suffix', 'vat_id']
        for field in optional_fields:
            value = getattr(self, field)
            if value is not None:
                data[field] = value

        return data


@dataclass
class CustomerGroup:
    """Група клієнтів."""
    id: Optional[int] = None
    code: str = ""
    tax_class_id: int = 3

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'CustomerGroup':
        """Створити з API відповіді."""
        return cls(
            id=data.get('id'),
            code=data.get('code', ''),
            tax_class_id=data.get('tax_class_id', 3)
        )


@dataclass
class Customer:
    """Модель клієнта Magento."""

    # Основні властивості
    id: Optional[int] = None
    group_id: int = 1
    default_billing: Optional[str] = None
    default_shipping: Optional[str] = None

    # Персональні дані
    firstname: str = ""
    lastname: str = ""
    middlename: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    email: str = ""
    dob: Optional[date] = None
    taxvat: Optional[str] = None
    gender: Optional[Gender] = None

    # Дати
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Колекції
    addresses: List[CustomerAddress] = field(default_factory=list)

    # Додаткові атрибути
    store_id: int = 1
    website_id: int = 1
    disable_auto_group_change: int = 0

    # Сирі дані
    _raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'Customer':
        """Створити клієнта з API відповіді."""
        customer = cls()

        # Основні поля
        customer.id = data.get('id')
        customer.group_id = data.get('group_id', 1)
        customer.default_billing = data.get('default_billing')
        customer.default_shipping = data.get('default_shipping')

        # Персональні дані
        customer.firstname = data.get('firstname', '')
        customer.lastname = data.get('lastname', '')
        customer.middlename = data.get('middlename')
        customer.prefix = data.get('prefix')
        customer.suffix = data.get('suffix')
        customer.email = data.get('email', '')
        customer.taxvat = data.get('taxvat')

        # Дата народження
        if 'dob' in data and data['dob']:
            customer.dob = datetime.fromisoformat(data['dob']).date()

        # Стать
        if 'gender' in data and data['gender']:
            try:
                customer.gender = Gender(data['gender'])
            except ValueError:
                pass  # Невідома стать

        # Дати
        if 'created_at' in data:
            customer.created_at = datetime.fromisoformat(
                data['created_at'].replace('Z', '+00:00')
            )
        if 'updated_at' in data:
            customer.updated_at = datetime.fromisoformat(
                data['updated_at'].replace('Z', '+00:00')
            )

        # Адреси
        if 'addresses' in data:
            customer.addresses = [
                CustomerAddress.from_api(addr) for addr in data['addresses']
            ]

        # Додаткові поля
        customer.store_id = data.get('store_id', 1)
        customer.website_id = data.get('website_id', 1)
        customer.disable_auto_group_change = data.get('disable_auto_group_change', 0)

        # Сирі дані
        customer._raw_data = data

        return customer

    def to_api(self) -> Dict[str, Any]:
        """Конвертувати в API формат."""
        data = {
            'group_id': self.group_id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email,
            'store_id': self.store_id,
            'website_id': self.website_id,
            'disable_auto_group_change': self.disable_auto_group_change
        }

        # Додаткові поля
        optional_fields = ['middlename', 'prefix', 'suffix', 'taxvat', 'default_billing', 'default_shipping']
        for field in optional_fields:
            value = getattr(self, field)
            if value is not None:
                data[field] = value

        # Дата народження
        if self.dob:
            data['dob'] = self.dob.isoformat()

        # Стать
        if self.gender:
            data['gender'] = self.gender.value

        # Адреси
        if self.addresses:
            data['addresses'] = [addr.to_api() for addr in self.addresses]

        return data

    def get_full_name(self) -> str:
        """Отримати повне ім'я."""
        parts = []
        if self.prefix:
            parts.append(self.prefix)
        if self.firstname:
            parts.append(self.firstname)
        if self.middlename:
            parts.append(self.middlename)
        if self.lastname:
            parts.append(self.lastname)
        if self.suffix:
            parts.append(self.suffix)
        return ' '.join(parts)

    def get_billing_address(self) -> Optional[CustomerAddress]:
        """Отримати адресу для виставлення рахунків."""
        for addr in self.addresses:
            if addr.default_billing:
                return addr
        return None

    def get_shipping_address(self) -> Optional[CustomerAddress]:
        """Отримати адресу доставки."""
        for addr in self.addresses:
            if addr.default_shipping:
                return addr
        return None

    def __str__(self) -> str:
        return f"Customer(email='{self.email}', name='{self.get_full_name()}')"
