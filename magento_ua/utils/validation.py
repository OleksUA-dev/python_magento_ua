"""
Валідатори для Magento бібліотеки.
"""

import re
from typing import Any, Dict, List, Optional, Union


class ValidationError(Exception):
    """Виняток для помилок валідації."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(message)


def validate_sku(sku: str) -> bool:
    """
    Валідує SKU товару.

    Args:
        sku: SKU для валідації

    Returns:
        True якщо SKU валідний

    Raises:
        ValidationError: Якщо SKU не валідний
    """
    if not sku:
        raise ValidationError("SKU не може бути порожнім", "sku")

    if not isinstance(sku, str):
        raise ValidationError("SKU має бути рядком", "sku")

    if len(sku) < 1 or len(sku) > 64:
        raise ValidationError("SKU має бути від 1 до 64 символів", "sku")

    # SKU може містити літери, цифри, дефіси та підкреслення
    if not re.match(r'^[a-zA-Z0-9_-]+$', sku):
        raise ValidationError(
            "SKU може містити тільки літери, цифри, дефіси та підкреслення",
            "sku"
        )

    return True


def validate_email_address(email: str) -> bool:
    """
    Валідує email адресу.

    Args:
        email: Email для валідації

    Returns:
        True якщо email валідний

    Raises:
        ValidationError: Якщо email не валідний
    """
    if not email:
        raise ValidationError("Email не може бути порожнім", "email")

    if not isinstance(email, str):
        raise ValidationError("Email має бути рядком", "email")

    # Базова регулярка для email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'


def validate_phone(phone: str, country_code: str = "UA") -> bool:
    """
    Валідує номер телефону.

    Args:
        phone: Номер телефону
        country_code: Код країни

    Returns:
        True якщо номер валідний

    Raises:
        ValidationError: Якщо номер не валідний
    """
    if not phone:
        raise ValidationError("Номер телефону не може бути порожнім", "phone")

    # Видаляємо всі символи крім цифр і +
    clean_phone = re.sub(r'[^\d+]', '', phone)

    if country_code == "UA":
        # Українські номери: +380XXXXXXXXX або 380XXXXXXXXX або 0XXXXXXXXX
        patterns = [
            r'^\+380\d{9}$',  # +380XXXXXXXXX
            r'^380\d{9}$',    # 380XXXXXXXXX
            r'^0\d{9}$'       # 0XXXXXXXXX
        ]

        if not any(re.match(pattern, clean_phone) for pattern in patterns):
            raise ValidationError(
                "Невалідний український номер телефону. "
                "Формат: +380XXXXXXXXX, 380XXXXXXXXX або 0XXXXXXXXX",
                "phone"
            )
    else:
        # Загальна перевірка міжнародних номерів
        if not re.match(r'^\+?\d{7,15}$', clean_phone):
            raise ValidationError(
                "Невалідний номер телефону. Має містити від 7 до 15 цифр",
                "phone"
            )

    return True


def validate_price(price: Union[int, float, str]) -> bool:
    """
    Валідує ціну.

    Args:
        price: Ціна для валідації

    Returns:
        True якщо ціна валідна

    Raises:
        ValidationError: Якщо ціна не валідна
    """
    if price is None:
        raise ValidationError("Ціна не може бути None", "price")

    try:
        price_float = float(price)
    except (ValueError, TypeError):
        raise ValidationError("Ціна має бути числом", "price")

    if price_float < 0:
        raise ValidationError("Ціна не може бути від'ємною", "price")

    if price_float > 999999999.99:
        raise ValidationError("Ціна занадто велика", "price")

    # Перевіряємо кількість десяткових знаків
    price_str = str(price_float)
    if '.' in price_str:
        decimal_places = len(price_str.split('.')[1])
        if decimal_places > 4:
            raise ValidationError("Ціна може мати максимум 4 десяткові знаки", "price")

    return True


def validate_weight(weight: Union[int, float, str]) -> bool:
    """
    Валідує вагу товару.

    Args:
        weight: Вага для валідації

    Returns:
        True якщо вага валідна

    Raises:
        ValidationError: Якщо вага не валідна
    """
    if weight is None:
        return True  # Вага може бути None

    try:
        weight_float = float(weight)
    except (ValueError, TypeError):
        raise ValidationError("Вага має бути числом", "weight")

    if weight_float < 0:
        raise ValidationError("Вага не може бути від'ємною", "weight")

    if weight_float > 999999:
        raise ValidationError("Вага занадто велика", "weight")

    return True


def validate_status(status: Union[int, str]) -> bool:
    """
    Валідує статус товару.

    Args:
        status: Статус (1 - активний, 2 - неактивний)

    Returns:
        True якщо статус валідний

    Raises:
        ValidationError: Якщо статус не валідний
    """
    try:
        status_int = int(status)
    except (ValueError, TypeError):
        raise ValidationError("Статус має бути числом", "status")

    if status_int not in [1, 2]:
        raise ValidationError("Статус має бути 1 (активний) або 2 (неактивний)", "status")

    return True


def validate_visibility(visibility: Union[int, str]) -> bool:
    """
    Валідує видимість товару.

    Args:
        visibility: Видимість (1-4)

    Returns:
        True якщо видимість валідна

    Raises:
        ValidationError: Якщо видимість не валідна
    """
    try:
        visibility_int = int(visibility)
    except (ValueError, TypeError):
        raise ValidationError("Видимість має бути числом", "visibility")

    # 1 - Not Visible Individually
    # 2 - Catalog
    # 3 - Search
    # 4 - Catalog, Search
    if visibility_int not in [1, 2, 3, 4]:
        raise ValidationError("Видимість має бути від 1 до 4", "visibility")

    return True


def validate_url_key(url_key: str) -> bool:
    """
    Валідує URL ключ.

    Args:
        url_key: URL ключ для валідації

    Returns:
        True якщо URL ключ валідний

    Raises:
        ValidationError: Якщо URL ключ не валідний
    """
    if not url_key:
        return True  # URL ключ може бути порожнім

    if not isinstance(url_key, str):
        raise ValidationError("URL ключ має бути рядком", "url_key")

    if len(url_key) > 255:
        raise ValidationError("URL ключ занадто довгий (максимум 255 символів)", "url_key")

    # URL ключ може містити тільки літери, цифри та дефіси
    if not re.match(r'^[a-z0-9-]+$', url_key):
        raise ValidationError(
            "URL ключ може містити тільки малі літери, цифри та дефіси",
            "url_key"
        )

    # Не може починатися або закінчуватися дефісом
    if url_key.startswith('-') or url_key.endswith('-'):
        raise ValidationError(
            "URL ключ не може починатися або закінчуватися дефісом",
            "url_key"
        )

    # Не може містити подвійні дефіси
    if '--' in url_key:
        raise ValidationError("URL ключ не може містити подвійні дефіси", "url_key")

    return True


def validate_attribute_set_id(attribute_set_id: Union[int, str]) -> bool:
    """
    Валідує ID набору атрибутів.

    Args:
        attribute_set_id: ID набору атрибутів

    Returns:
        True якщо ID валідний

    Raises:
        ValidationError: Якщо ID не валідний
    """
    try:
        id_int = int(attribute_set_id)
    except (ValueError, TypeError):
        raise ValidationError("ID набору атрибутів має бути числом", "attribute_set_id")

    if id_int <= 0:
        raise ValidationError("ID набору атрибутів має бути додатнім числом", "attribute_set_id")

    return True


def validate_product_type(product_type: str) -> bool:
    """
    Валідує тип товару.

    Args:
        product_type: Тип товару

    Returns:
        True якщо тип валідний

    Raises:
        ValidationError: Якщо тип не валідний
    """
    valid_types = [
        'simple',
        'configurable',
        'grouped',
        'virtual',
        'bundle',
        'downloadable'
    ]

    if product_type not in valid_types:
        raise ValidationError(
            f"Невалідний тип товару. Доступні: {', '.join(valid_types)}",
            "product_type"
        )

    return True


def validate_product_data(data: Dict[str, Any]) -> bool:
    """
    Валідує дані товару.

    Args:
        data: Дані товару

    Returns:
        True якщо всі дані валідні

    Raises:
        ValidationError: Якщо якісь дані не валідні
    """
    # Обов'язкові поля
    required_fields = ['sku', 'name', 'attribute_set_id', 'type_id']

    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f"Поле '{field}' є обов'язковим", field)

    # Валідація окремих полів
    validate_sku(data['sku'])
    validate_attribute_set_id(data['attribute_set_id'])
    validate_product_type(data['type_id'])

    # Опціональні поля
    if 'price' in data and data['price'] is not None:
        validate_price(data['price'])

    if 'weight' in data:
        validate_weight(data['weight'])

    if 'status' in data:
        validate_status(data['status'])

    if 'visibility' in data:
        validate_visibility(data['visibility'])

    if 'url_key' in data:
        validate_url_key(data['url_key'])

    return True


def validate_customer_data(data: Dict[str, Any]) -> bool:
    """
    Валідує дані клієнта.

    Args:
        data: Дані клієнта

    Returns:
        True якщо всі дані валідні

    Raises:
        ValidationError: Якщо якісь дані не валідні
    """
    # Обов'язкові поля
    required_fields = ['email', 'firstname', 'lastname']

    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f"Поле '{field}' є обов'язковим", field)

    # Валідація email
    validate_email_address(data['email'])

    # Валідація імені та прізвища
    if len(data['firstname']) < 1 or len(data['firstname']) > 255:
        raise ValidationError("Ім'я має бути від 1 до 255 символів", "firstname")

    if len(data['lastname']) < 1 or len(data['lastname']) > 255:
        raise ValidationError("Прізвище має бути від 1 до 255 символів", "lastname")

    # Валідація телефону (якщо вказаний)
    if 'telephone' in data and data['telephone']:
        validate_phone(data['telephone'])

    return True


def validate_search_criteria(criteria: Dict[str, Any]) -> bool:
    """
    Валідує критерії пошуку.

    Args:
        criteria: Критерії пошуку

    Returns:
        True якщо критерії валідні

    Raises:
        ValidationError: Якщо критерії не валідні
    """
    # Валідація page_size
    if 'page_size' in criteria:
        try:
            page_size = int(criteria['page_size'])
            if page_size <= 0 or page_size > 1000:
                raise ValidationError(
                    "page_size має бути від 1 до 1000",
                    "page_size"
                )
        except (ValueError, TypeError):
            raise ValidationError("page_size має бути числом", "page_size")

    # Валідація current_page
    if 'current_page' in criteria:
        try:
            current_page = int(criteria['current_page'])
            if current_page <= 0:
                raise ValidationError(
                    "current_page має бути додатнім числом",
                    "current_page"
                )
        except (ValueError, TypeError):
            raise ValidationError("current_page має бути числом", "current_page")

    return True

    if not re.match(email_pattern, email):
        raise ValidationError("Невалідний формат email адреси", "email")

    # Додаткові перевірки
    if len(email) > 254:  # RFC 5321
        raise ValidationError("Email адреса занадто довга", "email")

    local_part, domain = email.rsplit('@', 1)

    if len(local_part) > 64:  # RFC 5321
        raise ValidationError("Локальна частина email занадто довга", "email")

    if len(domain) > 253:  # RFC 1035
        raise ValidationError("Доменна частина email занадто довга", "email")

    return True


def validate_phone(phone: str, country_code: str = "UA") -> bool:
    """
    Валідує номер телефону.

    Args:
        phone: Номер телефону
        country_code: Код країни

    Returns:
        True якщо номер валідний

    Raises:
        ValidationError: Якщо номер не валідний
    """
    if not phone:
        raise ValidationError("Номер телефону не може бути порожнім", "phone")

    # Видаляємо всі символи крім цифр і +
    clean_phone = re.sub(r'[^\d+]', '', phone)

    if country_code == "UA":
        # Українські номери: +380XXXXXXXXX або 380XXXXXXXXX або 0XXXXXXXXX
        patterns = [
            r'^\+380\d{9}$',  # +380XXXXXXXXX
            r'^380\d{9}$',    # 380XXXXXXXXX
            r'^0\d{9}$'       # 0XXXXXXXXX
        ]

        if not any(re.match(pattern, clean_phone) for pattern in patterns):
            raise ValidationError(
                "Невалідний український номер телефону. "
                "Формат: +380XXXXXXXXX, 380XXXXXXXXX або 0XXXXXXXXX",
                "phone"
            )
    else:
        # Загальна перевірка міжнародних номерів
        if not re.match(r'^\+?\d{7,15}$', clean_phone):
            raise ValidationError(
                "Невалідний номер телефону. Має містити від 7 до 15 цифр",
                "phone"
            )

    return True


def validate_price(price: Union[int, float, str]) -> bool:
    """
    Валідує ціну.

    Args:
        price: Ціна для валідації

    Returns:
        True якщо ціна валідна

    Raises:
        ValidationError: Якщо ціна не валідна
    """
    if price is None:
        raise ValidationError("Ціна не може бути None", "price")

    try:
        price_float = float(price)
    except (ValueError, TypeError):
        raise ValidationError("Ціна має бути числом", "price")

    if price_float < 0:
        raise ValidationError("Ціна не може бути від'ємною", "price")

    if price_float > 999999999.99:
        raise ValidationError("Ціна занадто велика", "price")

    # Перевіряємо кількість десяткових знаків
    price_str = str(price_float)
    if '.' in price_str:
        decimal_places = len(price_str.split('.')[1])
        if decimal_places > 4:
            raise ValidationError("Ціна може мати максимум 4 десяткові знаки", "price")

    return True


def validate_weight(weight: Union[int, float, str]) -> bool:
    """
    Валідує вагу товару.

    Args:
        weight: Вага для валідації

    Returns:
        True якщо вага валідна

    Raises:
        ValidationError: Якщо вага не валідна
    """
    if weight is None:
        return True  # Вага може бути None

    try:
        weight_float = float(weight)
    except (ValueError, TypeError):
        raise ValidationError("Вага має бути числом", "weight")

    if weight_float < 0:
        raise ValidationError("Вага не може бути від'ємною", "weight")

    if weight_float > 999999:
        raise ValidationError("Вага занадто велика", "weight")

    return True


def validate_status(status: Union[int, str]) -> bool:
    """
    Валідує статус товару.

    Args:
        status: Статус (1 - активний, 2 - неактивний)

    Returns:
        True якщо статус валідний

    Raises:
        ValidationError: Якщо статус не валідний
    """
    try:
        status_int = int(status)
    except (ValueError, TypeError):
        raise ValidationError("Статус має бути числом", "status")

    if status_int not in [1, 2]:
        raise ValidationError("Статус має бути 1 (активний) або 2 (неактивний)", "status")

    return True


def validate_visibility(visibility: Union[int, str]) -> bool:
    """
    Валідує видимість товару.

    Args:
        visibility: Видимість (1-4)

    Returns:
        True якщо видимість валідна

    Raises:
        ValidationError: Якщо видимість не валідна
    """
    try:
        visibility_int = int(visibility)
    except (ValueError, TypeError):
        raise ValidationError("Видимість має бути числом", "visibility")

    # 1 - Not Visible Individually
    # 2 - Catalog
    # 3 - Search
    # 4 - Catalog, Search
    if visibility_int not in [1, 2, 3, 4]:
        raise ValidationError("Видимість має бути від 1 до 4", "visibility")

    return True


def validate_url_key(url_key: str) -> bool:
    """
    Валідує URL ключ.

    Args:
        url_key: URL ключ для валідації

    Returns:
        True якщо URL ключ валідний

    Raises:
        ValidationError: Якщо URL ключ не валідний
    """
    if not url_key:
        return True  # URL ключ може бути порожнім

    if not isinstance(url_key, str):
        raise ValidationError("URL ключ має бути рядком", "url_key")

    if len(url_key) > 255:
        raise ValidationError("URL ключ занадто довгий (максимум 255 символів)", "url_key")

    # URL ключ може містити тільки літери, цифри та дефіси
    if not re.match(r'^[a-z0-9-]+$', url_key):
        raise ValidationError(
            "URL ключ може містити тільки малі літери, цифри та дефіси",
            "url_key"
        )

    # Не може починатися або закінчуватися дефісом
    if url_key.startswith('-') or url_key.endswith('-'):
        raise ValidationError(
            "URL ключ не може починатися або закінчуватися дефісом",
            "url_key"
        )

    # Не може містити подвійні дефіси
    if '--' in url_key:
        raise ValidationError("URL ключ не може містити подвійні дефіси", "url_key")

    return True


def validate_attribute_set_id(attribute_set_id: Union[int, str]) -> bool:
    """
    Валідує ID набору атрибутів.

    Args:
        attribute_set_id: ID набору атрибутів

    Returns:
        True якщо ID валідний

    Raises:
        ValidationError: Якщо ID не валідний
    """
    try:
        id_int = int(attribute_set_id)
    except (ValueError, TypeError):
        raise ValidationError("ID набору атрибутів має бути числом", "attribute_set_id")

    if id_int <= 0:
        raise ValidationError("ID набору атрибутів має бути додатнім числом", "attribute_set_id")

    return True


def validate_product_type(product_type: str) -> bool:
    """
    Валідує тип товару.

    Args:
        product_type: Тип товару

    Returns:
        True якщо тип валідний

    Raises:
        ValidationError: Якщо тип не валідний
    """
    valid_types = [
        'simple',
        'configurable',
        'grouped',
        'virtual',
        'bundle',
        'downloadable'
    ]

    if product_type not in valid_types:
        raise ValidationError(
            f"Невалідний тип товару. Доступні: {', '.join(valid_types)}",
            "product_type"
        )

    return True


def validate_product_data(data: Dict[str, Any]) -> bool:
    """
    Валідує дані товару.

    Args:
        data: Дані товару

    Returns:
        True якщо всі дані валідні

    Raises:
        ValidationError: Якщо якісь дані не валідні
    """
    # Обов'язкові поля
    required_fields = ['sku', 'name', 'attribute_set_id', 'type_id']

    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f"Поле '{field}' є обов'язковим", field)

    # Валідація окремих полів
    validate_sku(data['sku'])
    validate_attribute_set_id(data['attribute_set_id'])
    validate_product_type(data['type_id'])

    # Опціональні поля
    if 'price' in data and data['price'] is not None:
        validate_price(data['price'])

    if 'weight' in data:
        validate_weight(data['weight'])

    if 'status' in data:
        validate_status(data['status'])

    if 'visibility' in data:
        validate_visibility(data['visibility'])

    if 'url_key' in data:
        validate_url_key(data['url_key'])

    return True


def validate_customer_data(data: Dict[str, Any]) -> bool:
    """
    Валідує дані клієнта.

    Args:
        data: Дані клієнта

    Returns:
        True якщо всі дані валідні

    Raises:
        ValidationError: Якщо якісь дані не валідні
    """
    # Обов'язкові поля
    required_fields = ['email', 'firstname', 'lastname']

    for field in required_fields:
        if field not in data or not data[field]:
            raise ValidationError(f"Поле '{field}' є обов'язковим", field)

    # Валідація email
    validate_email_address(data['email'])

    # Валідація імені та прізвища
    if len(data['firstname']) < 1 or len(data['firstname']) > 255:
        raise ValidationError("Ім'я має бути від 1 до 255 символів", "firstname")

    if len(data['lastname']) < 1 or len(data['lastname']) > 255:
        raise ValidationError("Прізвище має бути від 1 до 255 символів", "lastname")

    # Валідація телефону (якщо вказаний)
    if 'telephone' in data and data['telephone']:
        validate_phone(data['telephone'])

    return True


def validate_search_criteria(criteria: Dict[str, Any]) -> bool:
    """
    Валідує критерії пошуку.

    Args:
        criteria: Критерії пошуку

    Returns:
        True якщо критерії валідні

    Raises:
        ValidationError: Якщо критерії не валідні
    """
    # Валідація page_size
    if 'page_size' in criteria:
        try:
            page_size = int(criteria['page_size'])
            if page_size <= 0 or page_size > 1000:
                raise ValidationError(
                    "page_size має бути від 1 до 1000",
                    "page_size"
                )
        except (ValueError, TypeError):
            raise ValidationError("page_size має бути числом", "page_size")

    # Валідація current_page
    if 'current_page' in criteria:
        try:
            current_page = int(criteria['current_page'])
            if current_page <= 0:
                raise ValidationError(
                    "current_page має бути додатнім числом",
                    "current_page"
                )
        except (ValueError, TypeError):
            raise ValidationError("current_page має бути числом", "current_page")

    return True