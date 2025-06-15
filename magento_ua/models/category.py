# models/category.py (продовження)
"""Модель категорії Magento."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class CategoryProduct:
    """Зв'язок категорії з товаром."""
    sku: str
    position: int = 0
    category_id: Optional[int] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'CategoryProduct':
        """Створити з API відповіді."""
        return cls(
            sku=data.get('sku', ''),
            position=data.get('position', 0),
            category_id=data.get('category_id')
        )


@dataclass
class Category:
    """Модель категорії Magento."""

    # Основні властивості
    id: Optional[int] = None
    parent_id: int = 0
    name: str = ""
    is_active: bool = True
    position: int = 0
    level: int = 0

    # SEO та мета дані
    url_key: Optional[str] = None
    url_path: Optional[str] = None
    meta_title: Optional[str] = None
    meta_keywords: Optional[str] = None
    meta_description: Optional[str] = None

    # Опис
    description: Optional[str] = None

    # Зображення
    image: Optional[str] = None

    # Налаштування відображення
    display_mode: str = "PRODUCTS"  # PRODUCTS, PAGE, PRODUCTS_AND_PAGE
    is_anchor: bool = False
    include_in_menu: bool = True

    # Дати
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Шлях в дереві категорій
    path: str = "1"
    children_count: int = 0

    # Дочірні категорії та товари
    children: List['Category'] = field(default_factory=list)
    product_links: List[CategoryProduct] = field(default_factory=list)

    # Сирі дані
    _raw_data: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'Category':
        """Створити категорію з API відповіді."""
        category = cls()

        # Основні поля
        category.id = data.get('id')
        category.parent_id = data.get('parent_id', 0)
        category.name = data.get('name', '')
        category.is_active = data.get('is_active', True)
        category.position = data.get('position', 0)
        category.level = data.get('level', 0)

        # SEO дані
        category.url_key = data.get('url_key')
        category.url_path = data.get('url_path')
        category.meta_title = data.get('meta_title')
        category.meta_keywords = data.get('meta_keywords')
        category.meta_description = data.get('meta_description')

        # Опис та зображення
        category.description = data.get('description')
        category.image = data.get('image')

        # Налаштування відображення
        category.display_mode = data.get('display_mode', 'PRODUCTS')
        category.is_anchor = data.get('is_anchor', False)
        category.include_in_menu = data.get('include_in_menu', True)

        # Дати
        if 'created_at' in data:
            category.created_at = datetime.fromisoformat(
                data['created_at'].replace('Z', '+00:00')
            )
        if 'updated_at' in data:
            category.updated_at = datetime.fromisoformat(
                data['updated_at'].replace('Z', '+00:00')
            )

        # Шлях
        category.path = data.get('path', '1')
        category.children_count = data.get('children_count', 0)

        # Дочірні категорії
        if 'children_data' in data:
            category.children = [
                Category.from_api(child) for child in data['children_data']
            ]

        # Товари в категорії
        if 'product_links' in data:
            category.product_links = [
                CategoryProduct.from_api(link) for link in data['product_links']
            ]

        # Сирі дані
        category._raw_data = data

        return category

    def to_api(self) -> Dict[str, Any]:
        """Конвертувати в API формат."""
        data = {
            'name': self.name,
            'is_active': self.is_active,
            'parent_id': self.parent_id,
            'position': self.position,
            'include_in_menu': self.include_in_menu,
            'is_anchor': self.is_anchor,
            'display_mode': self.display_mode
        }

        # Додаткові поля
        optional_fields = [
            'url_key', 'description', 'meta_title',
            'meta_keywords', 'meta_description', 'image'
        ]
        for field in optional_fields:
            value = getattr(self, field)
            if value is not None:
                data[field] = value

        return data

    def get_breadcrumbs(self) -> List[int]:
        """Отримати хлібні крихти (ID категорій від кореня)."""
        return [int(cat_id) for cat_id in self.path.split('/') if cat_id]

    def is_root(self) -> bool:
        """Перевірити чи є категорія кореневою."""
        return self.parent_id == 0 or self.parent_id == 1

    def get_product_skus(self) -> List[str]:
        """Отримати список SKU товарів в категорії."""
        return [link.sku for link in self.product_links]

    def __str__(self) -> str:
        return f"Category(id={self.id}, name='{self.name}', level={self.level})"