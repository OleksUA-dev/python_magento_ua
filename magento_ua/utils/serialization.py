"""
Модуль для серіалізації та десеріалізації даних.
"""

import json
import pickle
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union, Type
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum


class JSONEncoder(json.JSONEncoder):
    """Розширений JSON енкодер для спеціальних типів."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, Enum):
            return obj.value
        elif is_dataclass(obj):
            return serialize_model(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


class JSONDecoder(json.JSONDecoder):
    """Розширений JSON декодер."""

    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Обробляє об'єкти при десеріалізації."""
        # Автоматично конвертуємо ISO дати
        for key, value in obj.items():
            if isinstance(value, str):
                # Спробуємо розпізнати дату
                if self._is_iso_date(value):
                    try:
                        obj[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except ValueError:
                        pass  # Залишаємо як рядок
        return obj

    def _is_iso_date(self, value: str) -> bool:
        """Перевіряє чи схожий рядок на ISO дату."""
        iso_patterns = [
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
            r'^\d{4}-\d{2}-\d{2}'
        ]
        import re
        return any(re.match(pattern, value) for pattern in iso_patterns)


def serialize_to_json(obj: Any, indent: Optional[int] = None) -> str:
    """
    Серіалізує об'єкт у JSON.

    Args:
        obj: Об'єкт для серіалізації
        indent: Відступи для форматування

    Returns:
        JSON рядок
    """
    return json.dumps(obj, cls=JSONEncoder, indent=indent, ensure_ascii=False)


def deserialize_from_json(json_str: str) -> Any:
    """
    Десеріалізує JSON у об'єкт.

    Args:
        json_str: JSON рядок

    Returns:
        Десеріалізований об'єкт
    """
    return json.loads(json_str, cls=JSONDecoder)


def serialize_model(model: Any) -> Dict[str, Any]:
    """
    Серіалізує модель у словник.

    Args:
        model: Модель для серіалізації

    Returns:
        Словник з даними моделі
    """
    if is_dataclass(model):
        result = {}
        for field in fields(model):
            value = getattr(model, field.name)
            if value is not None:
                result[field.name] = _serialize_value(value)
        return result
    elif hasattr(model, '__dict__'):
        return {k: _serialize_value(v) for k, v in model.__dict__.items() if not k.startswith('_')}
    else:
        return model


def deserialize_model(data: Dict[str, Any], model_class: Type) -> Any:
    """
    Десеріалізує словник у модель.

    Args:
        data: Дані для десеріалізації
        model_class: Клас моделі

    Returns:
        Екземпляр моделі
    """
    if is_dataclass(model_class):
        # Отримуємо поля dataclass
        field_types = {f.name: f.type for f in fields(model_class)}
        kwargs = {}

        for field_name, field_type in field_types.items():
            if field_name in data:
                kwargs[field_name] = _deserialize_value(data[field_name], field_type)

        return model_class(**kwargs)
    else:
        # Для звичайних класів
        instance = model_class()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance


def _serialize_value(value: Any) -> Any:
    """Серіалізує значення."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, Enum):
        return value.value
    elif is_dataclass(value):
        return serialize_model(value)
    elif isinstance(value, (list, tuple)):
        return [_serialize_value(item) for item in value]
    elif isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    else:
        return value


def _deserialize_value(value: Any, target_type: Type) -> Any:
    """Десеріалізує значення в цільовий тип."""
    if value is None:
        return None

    # Обробка Optional типів
    if hasattr(target_type, '__origin__') and target_type.__origin__ is Union:
        # Знаходимо не-None тип
        args = target_type.__args__
        if len(args) == 2 and type(None) in args:
            target_type = next(arg for arg in args if arg is not type(None))

    # Обробка List типів
    if hasattr(target_type, '__origin__') and target_type.__origin__ is list:
        if isinstance(value, list):
            item_type = target_type.__args__[0] if target_type.__args__ else Any
            return [_deserialize_value(item, item_type) for item in value]

    # Обробка Dict типів
    if hasattr(target_type, '__origin__') and target_type.__origin__ is dict:
        if isinstance(value, dict):
            return value

    # Базові типи
    if target_type is datetime and isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return value
    elif target_type is date and isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            return value
    elif target_type is Decimal:
        return Decimal(str(value))
    elif isinstance(target_type, type) and issubclass(target_type, Enum):
        return target_type(value)
    elif is_dataclass(target_type):
        if isinstance(value, dict):
            return deserialize_model(value, target_type)

    return value


def serialize_to_binary(obj: Any) -> bytes:
    """
    Серіалізує об'єкт у бінарний формат.

    Args:
        obj: Об'єкт для серіалізації

    Returns:
        Бінарні дані
    """
    return pickle.dumps(obj)


def deserialize_from_binary(data: bytes) -> Any:
    """
    Десеріалізує бінарні дані у об'єкт.

    Args:
        data: Бінарні дані

    Returns:
        Десеріалізований об'єкт
    """
    return pickle.loads(data)


def to_magento_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Конвертує дані у формат Magento API.

    Args:
        data: Дані для конвертації

    Returns:
        Дані у форматі Magento
    """
    result = {}

    for key, value in data.items():
        # Конвертуємо snake_case в camelCase для деяких полів
        magento_key = _to_magento_key(key)

        if isinstance(value, dict):
            result[magento_key] = to_magento_format(value)
        elif isinstance(value, list):
            result[magento_key] = [
                to_magento_format(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[magento_key] = _to_magento_value(value)

    return result


def from_magento_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Конвертує дані з формату Magento API.

    Args:
        data: Дані у форматі Magento

    Returns:
        Нормалізовані дані
    """
    result = {}

    for key, value in data.items():
        # Конвертуємо camelCase в snake_case
        python_key = _from_magento_key(key)

        if isinstance(value, dict):
            result[python_key] = from_magento_format(value)
        elif isinstance(value, list):
            result[python_key] = [
                from_magento_format(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[python_key] = _from_magento_value(value)

    return result


def _to_magento_key(key: str) -> str:
    """Конвертує Python ключ у Magento формат."""
    # Деякі спеціальні випадки
    special_mappings = {
        'attribute_set_id': 'attribute_set_id',  # Залишаємо як є
        'type_id': 'type_id',  # Залишаємо як є
        'url_key': 'url_key',  # Залишаємо як є
    }

    if key in special_mappings:
        return special_mappings[key]

    # Загальна конвертація snake_case -> camelCase
    components = key.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def _from_magento_key(key: str) -> str:
    """Конвертує Magento ключ у Python формат."""
    import re

    # Спеціальні випадки (залишаємо як є)
    if '_' in key or key.islower():
        return key

    # Конвертація camelCase -> snake_case
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', key)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def _to_magento_value(value: Any) -> Any:
    """Конвертує значення у Magento формат."""
    if isinstance(value, bool):
        return 1 if value else 0
    elif isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, Decimal):
        return str(value)
    return value


def _from_magento_value(value: Any) -> Any:
    """Конвертує значення з Magento формату."""
    if isinstance(value, str):
        # Спробуємо розпізнати булеві значення
        if value in ('1', 'true', 'True'):
            return True
        elif value in ('0', 'false', 'False'):
            return False

        # Спробуємо розпізнати числа
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

    return value


def create_search_criteria(filters: Optional[Dict[str, Any]] = None,
                           sort_orders: Optional[List[Dict[str, str]]] = None,
                           page_size: Optional[int] = None,
                           current_page: Optional[int] = None) -> Dict[str, Any]:
    """
    Створює об'єкт searchCriteria для Magento API.

    Args:
        filters: Фільтри пошуку
        sort_orders: Порядок сортування
        page_size: Розмір сторінки
        current_page: Поточна сторінка

    Returns:
        Об'єкт searchCriteria
    """
    criteria = {}

    if filters:
        filter_groups = []
        for field, value in filters.items():
            if isinstance(value, list):
                # Фільтр IN
                filter_groups.append({
                    'filters': [{
                        'field': field,
                        'value': ','.join(str(v) for v in value),
                        'condition_type': 'in'
                    }]
                })
            else:
                # Фільтр EQ
                filter_groups.append({
                    'filters': [{
                        'field': field,
                        'value': str(value),
                        'condition_type': 'eq'
                    }]
                })

        criteria['filter_groups'] = filter_groups

    if sort_orders:
        criteria['sort_orders'] = sort_orders

    if page_size is not None:
        criteria['page_size'] = page_size

    if current_page is not None:
        criteria['current_page'] = current_page

    return {'searchCriteria': criteria}