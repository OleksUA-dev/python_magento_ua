"""Модель товару Magento."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class ProductImage:
    """Зображення товару."""
    id: Optional[int] = None
    media_type: str = "image"
    label: Optional[str] = None
    position: int = 0
    disabled: bool = False
    types: List[str] = field(default_factory=list)
    file: Optional[str] = None
    content: Optional[Dict[str, Any]] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'ProductImage':
        """Створити з API відповіді."""
        return cls(
            id=data.get('id'),
            media_type=data.get('media_type', 'image'),
            label=data.get('label'),
            position=data.get('position', 0),
            disabled=data.get('disabled', False),
            types=data.get('types', []),
            file=data.get('file'),
            content=data.get('content')
        )


@dataclass
class ProductAttribute:
    """Атрибут товару."""
    attribute_code: str
    value: Any
    attribute_type: Optional[str] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'ProductAttribute':
        """Створити з API відповіді."""
        return cls(
            attribute_code=data.get('attribute_code', ''),
            value=data.get('value'),
            attribute_type=data.get('attribute_type')
        )


@dataclass
class Product:
    """Модель товару Magento."""

    # Основні властивості
    id: Optional[int] = None
    sku: str = ""
    name: str = ""
    attribute_set_id: int = 4
    price: Decimal = field(default_factory=lambda: Decimal('0'))
    status: int = 1  # 1 = enabled, 2 = disabled
    visibility: int = 4  # 1=Not Visible, 2=Catalog, 3=Search, 4=Catalog+Search
    type_id: str = "simple"

    # Додаткові властивості
    weight: Optional[Decimal] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    url_key: Optional[str] = None

    # Дати
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Колекції
    categories: List[int] = field(default_factory=list)
    images: List[ProductImage] = field(default_factory=list)
    custom_attributes: List[ProductAttribute] = field(default_factory=list)

    # Інвентар
    qty: Optional[int] = None
    is_in_stock: bool = True
    manage_stock: bool = True
    use_config_manage_stock: bool = True

    # Сирі дані з API
    _raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'Product':
        """Створити товар з API відповіді."""
        product = cls()

        # Основні поля
        product.id = data.get('id')
        product.sku = data.get('sku', '')
        product.name = data.get('name', '')
        product.attribute_set_id = data.get('attribute_set_id', 4)
        product.status = data.get('status', 1)
        product.visibility = data.get('visibility', 4)
        product.type_id = data.get('type_id', 'simple')

        # Ціна
        if 'price' in data:
            product.price = Decimal(str(data['price']))

        # Вага
        if 'weight' in data:
            product.weight = Decimal(str(data['weight']))

        # Дати
        if 'created_at' in data:
            product.created_at = datetime.fromisoformat(
                data['created_at'].replace('Z', '+00:00')
            )
        if 'updated_at' in data:
            product.updated_at = datetime.fromisoformat(
                data['updated_at'].replace('Z', '+00:00')
            )

        # Категорії
        if 'category_links' in data:
            product.categories = [
                link['category_id'] for link in data['category_links']
            ]

        # Зображення
        if 'media_gallery_entries' in data:
            product.images = [
                ProductImage.from_api(img)
                for img in data['media_gallery_entries']
            ]

        # Кастомні атрибути
        if 'custom_attributes' in data:
            product.custom_attributes = [
                ProductAttribute.from_api(attr)
                for attr in data['custom_attributes']
            ]

        # Інвентар з extension_attributes
        if 'extension_attributes' in data:
            ext_attr = data['extension_attributes']
            if 'stock_item' in ext_attr:
                stock = ext_attr['stock_item']
                product.qty = stock.get('qty')
                product.is_in_stock = stock.get('is_in_stock', True)
                product.manage_stock = stock.get('manage_stock', True)
                product.use_config_manage_stock = stock.get('use_config_manage_stock', True)

        # Зберегти сирі дані
        product._raw_data = data

        return product

    def to_api(self) -> Dict[str, Any]:
        """Конвертувати в API формат."""
        data = {
            'sku': self.sku,
            'name': self.name,
            'attribute_set_id': self.attribute_set_id,
            'price': float(self.price),
            'status': self.status,
            'visibility': self.visibility,
            'type_id': self.type_id,
        }

        # Додаткові поля
        if self.weight is not None:
            data['weight'] = float(self.weight)
        if self.description:
            data['description'] = self.description
        if self.short_description:
            data['short_description'] = self.short_description
        if self.meta_title:
            data['meta_title'] = self.meta_title
        if self.meta_description:
            data['meta_description'] = self.meta_description
        if self.url_key:
            data['url_key'] = self.url_key

        # Кастомні атрибути
        if self.custom_attributes:
            data['custom_attributes'] = [
                {
                    'attribute_code': attr.attribute_code,
                    'value': attr.value
                }
                for attr in self.custom_attributes
            ]

        # Категорії
        if self.categories:
            data['category_links'] = [
                {'category_id': cat_id} for cat_id in self.categories
            ]

        return data

    def get_attribute_value(self, attribute_code: str) -> Any:
        """Отримати значення кастомного атрибуту."""
        for attr in self.custom_attributes:
            if attr.attribute_code == attribute_code:
                return attr.value
        return None

    def set_attribute_value(self, attribute_code: str, value: Any) -> None:
        """Встановити значення кастомного атрибуту."""
        for attr in self.custom_attributes:
            if attr.attribute_code == attribute_code:
                attr.value = value
                return
        # Додати новий атрибут
        self.custom_attributes.append(
            ProductAttribute(attribute_code=attribute_code, value=value)
        )

    def __str__(self) -> str:
        return f"Product(sku='{self.sku}', name='{self.name}', price={self.price})"
