"""Валідація даних для Magento API."""

import re
from typing import Any, List, Dict, Optional
from decimal import Decimal, InvalidOperation


class ValidationError(Exception):
    """Помилка валідації."""

    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        super().__init__(message)
        self.field = field
        self.value = value
        self.message = message

    def __str__(self) -> str:
        if self.field:
            return f"Validation error for field '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


def validate_sku(sku: str) -> str:
    """
    Валідація SKU товару.

    Args:
        sku: SKU для валідації

    Returns:
        Валідний SKU

    Raises:
        ValidationError: Якщо SKU невалідний
    """
    if not sku:
        raise ValidationError("SKU не може бути порожнім", field="sku", value=sku)

    if not isinstance(sku, str):
        raise ValidationError("SKU має бути рядком", field="sku", value=sku)

    # SKU не може містити пробіли
    if ' ' in sku:
        raise ValidationError("SKU не може містити пробіли", field="sku", value=sku)

    # Максимальна довжина SKU в Magento
    if len(sku) > 64:
        raise ValidationError("SKU не може бути довшим за 64 символи", field="sku", value=sku)

    # Дозволені символи: літери, цифри, дефіс, підкреслення
    if not re.match(r'^[a-zA-Z0-9_-]+$', sku):
        raise ValidationError(
            "SKU може містити тільки літери, цифри, дефіс та підкреслення",
            field="sku", value=sku
        )

    return sku.strip()


def validate_email(email: str) -> str:
    """
    Валідація email адреси.

    Args:
        email: Email для валідації

    Returns:
        Валідний email

    Raises:
        ValidationError: Якщо email невалідний
    """
    if not email:
        raise ValidationError("Email не може бути порожнім", field="email", value=email)

    if not isinstance(email, str):
        raise ValidationError("Email має бути рядком", field="email", value=email)

    # Простий regex для email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError("Невалідний формат email", field="email", value=email)

    return email.lower().strip()


def validate_phone(phone: str) -> str:
    """
    Валідація номера телефону.

    Args:
        phone: Номер телефону для валідації

    Returns:
        Валідний номер телефону

    Raises:
        ValidationError: Якщо номер невалідний
    """
    if not phone:
        raise ValidationError("Номер телефону не може бути порожнім", field="phone", value=phone)

    if not isinstance(phone, str):
        raise ValidationError("Номер телефону має бути рядком", field="phone", value=phone)

    # Очистити номер від пробілів, дефісів та дужок
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)

    # Перевірити, що залишилися тільки цифри та можливо + на початку
    if not re.match(r'^\+?[0-9]{7,15}$', clean_phone):
        raise ValidationError(
            "Номер телефону має містити від 7 до 15 цифр",
            field="phone", value=phone
        )

    return clean_phone


def validate_price(price: Any) -> Decimal:
    """
    Валідація ціни.

    Args:
        price: Ціна для валідації

    Returns:
        Валідна ціна як Decimal

    Raises:
        ValidationError: Якщо ціна невалідна
    """
    if price is None:
        raise ValidationError("Ціна не може бути None", field="price", value=price)

    try:
        decimal_price = Decimal(str(price))
    except (InvalidOperation, ValueError):
        raise ValidationError("Невалідний формат ціни", field="price", value=price)

    if decimal_price < 0:
        raise ValidationError("Ціна не може бути від'ємною", field="price", value=price)

    # Перевірити кількість знаків після коми (зазвичай максимум 4)
    if decimal_price.as_tuple().exponent < -4:
        raise ValidationError("Ціна може мати максимум 4 знаки після коми", field="price", value=price)

    return decimal_price


def validate_quantity(qty: Any) -> int:
    """
    Валідація кількості.

    Args:
        qty: Кількість для валідації

    Returns:
        Валідна кількість

    Raises:
        ValidationError: Якщо кількість невалідна
    """
    if qty is None:
        raise ValidationError("Кількість не може бути None", field="qty", value=qty)

    try:
        int_qty = int(qty)
    except (ValueError, TypeError):
        raise ValidationError("Кількість має бути цілим числом", field="qty", value=qty)

    if int_qty < 0:
        raise ValidationError("Кількість не може бути від'ємною", field="qty", value=qty)

    return int_qty


def validate_status(status: Any) -> int:
    """
    Валідація статусу товару.

    Args:
        status: Статус для валідації

    Returns:
        Валідний статус

    Raises:
        ValidationError: Якщо статус невалідний
    """
    if status is None:
        raise ValidationError("Статус не може бути None", field="status", value=status)

    try:
        int_status = int(status)
    except (ValueError, TypeError):
        raise ValidationError("Статус має бути цілим числом", field="status", value=status)

    if int_status not in [1, 2]:  # 1 = enabled, 2 = disabled
        raise ValidationError("Статус має бути 1 (enabled) або 2 (disabled)", field="status", value=status)

    return int_status


def validate_visibility(visibility: Any) -> int:
    """
    Валідація видимості товару.

    Args:
        visibility: Видимість для валідації

    Returns:
        Валідна видимість

    Raises:
        ValidationError: Якщо видимість невалідна
    """
    if visibility is None:
        raise ValidationError("Видимість не може бути None", field="visibility", value=visibility)

    try:
        int_visibility = int(visibility)
    except (ValueError, TypeError):
        raise ValidationError("Видимість має бути цілим числом", field="visibility", value=visibility)

    if int_visibility not in [1, 2, 3, 4]:  # 1=Not Visible, 2=Catalog, 3=Search, 4=Catalog+Search
        raise ValidationError(
            "Видимість має бути 1 (Not Visible), 2 (Catalog), 3 (Search) або 4 (Catalog+Search)",
            field="visibility", value=visibility
        )

    return int_visibility


class ProductValidator:
    """Валідатор для товарів."""

    @staticmethod
    def validate_product_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валідація даних товару.

        Args:
            data: Дані товару для валідації

        Returns:
            Валідні дані товару

        Raises:
            ValidationError: Якщо дані невалідні
        """
        validated_data = {}

        # Обов'язкові поля
        if 'sku' not in data:
            raise ValidationError("SKU є обов'язковим полем", field="sku")
        validated_data['sku'] = validate_sku(data['sku'])

        if 'name' not in data:
            raise ValidationError("Назва товару є обов'язковим полем", field="name")
        if not data['name'].strip():
            raise ValidationError("Назва товару не може бути порожньою", field="name")
        validated_data['name'] = data['name'].strip()

        # Додаткові поля
        if 'price' in data:
            validated_data['price'] = validate_price(data['price'])

        if 'status' in data:
            validated_data['status'] = validate_status(data['status'])

        if 'visibility' in data:
            validated_data['visibility'] = validate_visibility(data['visibility'])

        if 'weight' in data and data['weight'] is not None:
            validated_data['weight'] = validate_price(
                data['weight'])  # Використовуємо validate_price для позитивних чисел

        # Копіювати інші поля без змін
        for key, value in data.items():
            if key not in validated_data:
                validated_data[key] = value

        return validated_data


class CustomerValidator:
    """Валідатор для клієнтів."""

    @staticmethod
    def validate_customer_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валідація даних клієнта.

        Args:
            data: Дані клієнта для валідації

        Returns:
            Валідні дані клієнта

        Raises:
            ValidationError: Якщо дані невалідні
        """
        validated_data = {}

        # Обов'язкові поля
        if 'email' not in data:
            raise ValidationError("Email є обов'язковим полем", field="email")
        validated_data['email'] = validate_email(data['email'])

        if 'firstname' not in data:
            raise ValidationError("Ім'я є обов'язковим полем", field="firstname")
        if not data['firstname'].strip():
            raise ValidationError("Ім'я не може бути порожнім", field="firstname")
        validated_data['firstname'] = data['firstname'].strip()

        if 'lastname' not in data:
            raise ValidationError("Прізвище є обов'язковим полем", field="lastname")
        if not data['lastname'].strip():
            raise ValidationError("Прізвище не може бути порожнім", field="lastname")
        validated_data['lastname'] = data['lastname'].strip()

        # Додаткові поля
        if 'middlename' in data and data['middlename']:
            validated_data['middlename'] = data['middlename'].strip()

        if 'prefix' in data and data['prefix']:
            validated_data['prefix'] = data['prefix'].strip()

        if 'suffix' in data and data['suffix']:
            validated_data['suffix'] = data['suffix'].strip()

        if 'dob' in data and data['dob']:
            # Валідація дати народження
            from datetime import datetime
            try:
                if isinstance(data['dob'], str):
                    datetime.fromisoformat(data['dob'])
                validated_data['dob'] = data['dob']
            except ValueError:
                raise ValidationError("Невалідний формат дати народження", field="dob", value=data['dob'])

        if 'gender' in data and data['gender'] is not None:
            gender = int(data['gender'])
            if gender not in [1, 2, 3]:  # 1=Male, 2=Female, 3=Not Specified
                raise ValidationError("Стать має бути 1 (чоловіча), 2 (жіноча) або 3 (не вказано)", field="gender",
                                      value=data['gender'])
            validated_data['gender'] = gender

        if 'group_id' in data:
            group_id = int(data['group_id'])
            if group_id < 0:
                raise ValidationError("ID групи клієнтів не може бути від'ємним", field="group_id",
                                      value=data['group_id'])
            validated_data['group_id'] = group_id

        if 'store_id' in data:
            store_id = int(data['store_id'])
            if store_id < 0:
                raise ValidationError("ID магазину не може бути від'ємним", field="store_id", value=data['store_id'])
            validated_data['store_id'] = store_id

        if 'website_id' in data:
            website_id = int(data['website_id'])
            if website_id < 0:
                raise ValidationError("ID веб-сайту не може бути від'ємним", field="website_id",
                                      value=data['website_id'])
            validated_data['website_id'] = website_id

        # Валідація адрес
        if 'addresses' in data and data['addresses']:
            validated_addresses = []
            for i, address in enumerate(data['addresses']):
                try:
                    validated_address = CustomerValidator.validate_address_data(address)
                    validated_addresses.append(validated_address)
                except ValidationError as e:
                    raise ValidationError(f"Помилка в адресі {i + 1}: {e.message}", field=f"addresses[{i}]")
            validated_data['addresses'] = validated_addresses

        # Копіювати інші поля без змін
        for key, value in data.items():
            if key not in validated_data:
                validated_data[key] = value

        return validated_data

    @staticmethod
    def validate_address_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валідація даних адреси клієнта.

        Args:
            data: Дані адреси для валідації

        Returns:
            Валідні дані адреси

        Raises:
            ValidationError: Якщо дані невалідні
        """
        validated_data = {}

        # Обов'язкові поля для адреси
        required_fields = ['firstname', 'lastname', 'street', 'city', 'postcode', 'country_id']

        for field in required_fields:
            if field not in data or not data[field]:
                field_names = {
                    'firstname': "Ім'я",
                    'lastname': "Прізвище",
                    'street': "Вулиця",
                    'city': "Місто",
                    'postcode': "Поштовий індекс",
                    'country_id': "Код країни"
                }
                raise ValidationError(f"{field_names.get(field, field)} є обов'язковим полем для адреси", field=field)

        validated_data['firstname'] = data['firstname'].strip()
        validated_data['lastname'] = data['lastname'].strip()
        validated_data['city'] = data['city'].strip()
        validated_data['postcode'] = data['postcode'].strip()
        validated_data['country_id'] = data['country_id'].strip().upper()

        # Вулиця має бути списком
        if isinstance(data['street'], str):
            validated_data['street'] = [data['street'].strip()]
        elif isinstance(data['street'], list):
            validated_data['street'] = [s.strip() for s in data['street'] if s.strip()]
        else:
            raise ValidationError("Вулиця має бути рядком або списком рядків", field="street", value=data['street'])

        # Валідація коду країни (ISO 2-letter code)
        if len(validated_data['country_id']) != 2:
            raise ValidationError("Код країни має бути 2-символьним (ISO)", field="country_id",
                                  value=data['country_id'])

        # Додаткові поля
        if 'company' in data and data['company']:
            validated_data['company'] = data['company'].strip()

        if 'telephone' in data and data['telephone']:
            validated_data['telephone'] = validate_phone(data['telephone'])

        if 'fax' in data and data['fax']:
            validated_data['fax'] = validate_phone(data['fax'])

        if 'middlename' in data and data['middlename']:
            validated_data['middlename'] = data['middlename'].strip()

        if 'prefix' in data and data['prefix']:
            validated_data['prefix'] = data['prefix'].strip()

        if 'suffix' in data and data['suffix']:
            validated_data['suffix'] = data['suffix'].strip()

        if 'vat_id' in data and data['vat_id']:
            validated_data['vat_id'] = data['vat_id'].strip()

        if 'region' in data and data['region']:
            validated_data['region'] = data['region'].strip()

        if 'region_id' in data and data['region_id'] is not None:
            region_id = int(data['region_id'])
            if region_id < 0:
                raise ValidationError("ID регіону не може бути від'ємним", field="region_id", value=data['region_id'])
            validated_data['region_id'] = region_id

        # Булеві поля
        validated_data['default_shipping'] = bool(data.get('default_shipping', False))
        validated_data['default_billing'] = bool(data.get('default_billing', False))

        # Копіювати інші поля без змін
        for key, value in data.items():
            if key not in validated_data:
                validated_data[key] = value

        return validated_data


class OrderValidator:
    """Валідатор для замовлень."""

    @staticmethod
    def validate_order_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валідація даних замовлення.

        Args:
            data: Дані замовлення для валідації

        Returns:
            Валідні дані замовлення

        Raises:
            ValidationError: Якщо дані невалідні
        """
        validated_data = {}

        # Валідація статусу замовлення
        if 'status' in data:
            valid_statuses = [
                'pending', 'processing', 'complete', 'canceled',
                'closed', 'fraud', 'holded', 'payment_review'
            ]
            if data['status'] not in valid_statuses:
                raise ValidationError(f"Невалідний статус замовлення. Допустимі: {', '.join(valid_statuses)}",
                                      field="status", value=data['status'])
            validated_data['status'] = data['status']

        # Валідація стану замовлення
        if 'state' in data:
            valid_states = ['new', 'pending_payment', 'processing', 'complete', 'canceled', 'closed']
            if data['state'] not in valid_states:
                raise ValidationError(f"Невалідний стан замовлення. Допустимі: {', '.join(valid_states)}",
                                      field="state", value=data['state'])
            validated_data['state'] = data['state']

        # Валідація email клієнта
        if 'customer_email' in data and data['customer_email']:
            validated_data['customer_email'] = validate_email(data['customer_email'])

        # Валідація фінансових полів
        financial_fields = [
            'base_grand_total', 'grand_total', 'base_subtotal', 'subtotal',
            'base_tax_amount', 'tax_amount', 'base_shipping_amount', 'shipping_amount',
            'base_discount_amount', 'discount_amount'
        ]

        for field in financial_fields:
            if field in data and data[field] is not None:
                try:
                    validated_data[field] = validate_price(data[field])
                except ValidationError as e:
                    raise ValidationError(f"Помилка в полі {field}: {e.message}", field=field, value=data[field])

        # Валідація валют
        if 'base_currency_code' in data:
            currency = data['base_currency_code'].upper()
            if len(currency) != 3:
                raise ValidationError("Код валюти має бути 3-символьним", field="base_currency_code",
                                      value=data['base_currency_code'])
            validated_data['base_currency_code'] = currency

        if 'order_currency_code' in data:
            currency = data['order_currency_code'].upper()
            if len(currency) != 3:
                raise ValidationError("Код валюти має бути 3-символьним", field="order_currency_code",
                                      value=data['order_currency_code'])
            validated_data['order_currency_code'] = currency

        # Валідація товарів замовлення
        if 'items' in data and data['items']:
            validated_items = []
            for i, item in enumerate(data['items']):
                try:
                    validated_item = OrderValidator.validate_order_item_data(item)
                    validated_items.append(validated_item)
                except ValidationError as e:
                    raise ValidationError(f"Помилка в товарі {i + 1}: {e.message}", field=f"items[{i}]")
            validated_data['items'] = validated_items

        # Копіювати інші поля без змін
        for key, value in data.items():
            if key not in validated_data:
                validated_data[key] = value

        return validated_data

    @staticmethod
    def validate_order_item_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валідація даних товару в замовленні.

        Args:
            data: Дані товару в замовленні

        Returns:
            Валідні дані товару

        Raises:
            ValidationError: Якщо дані невалідні
        """
        validated_data = {}

        # Обов'язкові поля
        if 'sku' not in data or not data['sku']:
            raise ValidationError("SKU товару є обов'язковим", field="sku")
        validated_data['sku'] = validate_sku(data['sku'])

        if 'name' not in data or not data['name']:
            raise ValidationError("Назва товару є обов'язковою", field="name")
        validated_data['name'] = data['name'].strip()

        # Валідація кількості
        if 'qty_ordered' in data:
            try:
                qty = Decimal(str(data['qty_ordered']))
                if qty < 0:
                    raise ValidationError("Кількість не може бути від'ємною", field="qty_ordered",
                                          value=data['qty_ordered'])
                validated_data['qty_ordered'] = qty
            except (InvalidOperation, ValueError):
                raise ValidationError("Невалідний формат кількості", field="qty_ordered", value=data['qty_ordered'])

        # Валідація цін
        price_fields = ['price', 'row_total', 'base_price', 'base_row_total']
        for field in price_fields:
            if field in data and data[field] is not None:
                try:
                    validated_data[field] = validate_price(data[field])
                except ValidationError as e:
                    raise ValidationError(f"Помилка в полі {field}: {e.message}", field=field, value=data[field])

        # Валідація типу товару
        if 'product_type' in data:
            valid_types = ['simple', 'configurable', 'grouped', 'virtual', 'bundle', 'downloadable']
            if data['product_type'] not in valid_types:
                raise ValidationError(f"Невалідний тип товару. Допустимі: {', '.join(valid_types)}",
                                      field="product_type", value=data['product_type'])
            validated_data['product_type'] = data['product_type']

        # Копіювати інші поля без змін
        for key, value in data.items():
            if key not in validated_data:
                validated_data[key] = value

        return validated_data


def validate_magento_data(entity_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Універсальна функція валідації даних для різних типів сутностей Magento.

    Args:
        entity_type: Тип сутності ('product', 'customer', 'order')
        data: Дані для валідації

    Returns:
        Валідні дані

    Raises:
        ValidationError: Якщо дані невалідні
    """
    validators = {
        'product': ProductValidator.validate_product_data,
        'customer': CustomerValidator.validate_customer_data,
        'order': OrderValidator.validate_order_data
    }

    if entity_type not in validators:
        raise ValidationError(f"Невідомий тип сутності: {entity_type}")

    return validators[entity_type](data)


# Приклади використання
if __name__ == "__main__":
    # Приклад валідації товару
    try:
        product_data = {
            'sku': 'test-product-001',
            'name': 'Тестовий товар',
            'price': '99.99',
            'status': 1,
            'visibility': 4
        }

        validated_product = ProductValidator.validate_product_data(product_data)
        print("Товар валідний:", validated_product)

    except ValidationError as e:
        print(f"Помилка валідації товару: {e}")

    # Приклад валідації клієнта
    try:
        customer_data = {
            'email': 'test@example.com',
            'firstname': 'Іван',
            'lastname': 'Петренко',
            'addresses': [{
                'firstname': 'Іван',
                'lastname': 'Петренко',
                'street': ['вул. Хрещатик, 1'],
                'city': 'Київ',
                'postcode': '01001',
                'country_id': 'UA',
                'telephone': '+380501234567',
                'default_shipping': True,
                'default_billing': True
            }]
        }

        validated_customer = CustomerValidator.validate_customer_data(customer_data)
        print("Клієнт валідний:", validated_customer)

    except ValidationError as e:
        print(f"Помилка валідації клієнта: {e}")