"""
Допоміжні функції для Magento бібліотеки.
"""

import re
import html
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin, urlparse
import hashlib
import secrets
import string


def format_price(price: Union[int, float, str], currency: str = "UAH") -> str:
    """
    Форматує ціну з валютою.

    Args:
        price: Ціна для форматування
        currency: Код валюти

    Returns:
        Відформатована ціна з валютою
    """
    try:
        price_float = float(price)
        return f"{price_float:.2f} {currency}"
    except (ValueError, TypeError):
        return f"0.00 {currency}"


def parse_date(date_string: str) -> Optional[datetime]:
    """
    Парсить дату з рядка у різних форматах.

    Args:
        date_string: Рядок з датою

    Returns:
        Об'єкт datetime або None
    """
    if not date_string:
        return None

    # Список можливих форматів дат
    date_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%d/%m/%Y",
        "%d.%m.%Y",
        "%d-%m-%Y",
    ]

    for date_format in date_formats:
        try:
            return datetime.strptime(date_string, date_format)
        except ValueError:
            continue

    return None


def generate_url_key(name: str) -> str:
    """
    Генерує URL ключ з назви товару/категорії.

    Args:
        name: Назва для перетворення

    Returns:
        URL-friendly рядок
    """
    if not name:
        return ""

    # Заміна українських символів на латинські
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g',
        'д': 'd', 'е': 'e', 'є': 'ye', 'ж': 'zh', 'з': 'z',
        'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y', 'к': 'k',
        'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
        'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
        'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ь': '', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G',
        'Д': 'D', 'Е': 'E', 'Є': 'YE', 'Ж': 'ZH', 'З': 'Z',
        'И': 'Y', 'І': 'I', 'Ї': 'YI', 'Й': 'Y', 'К': 'K',
        'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P',
        'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F',
        'Х': 'KH', 'Ц': 'TS', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SHCH',
        'Ь': '', 'Ю': 'YU', 'Я': 'YA'
    }

    # Транслітерація
    result = ""
    for char in name:
        result += translit_map.get(char, char)

    # Очищення та форматування
    result = result.lower()
    result = re.sub(r'[^a-z0-9\s-]', '', result)
    result = re.sub(r'[\s-]+', '-', result)
    result = result.strip('-')

    return result


def clean_html(html_string: str) -> str:
    """
    Очищує HTML теги з рядка.

    Args:
        html_string: Рядок з HTML

    Returns:
        Очищений текст
    """
    if not html_string:
        return ""

    # Заміна HTML entities
    clean_text = html.unescape(html_string)

    # Видалення HTML тегів
    clean_text = re.sub(r'<[^>]+>', '', clean_text)

    # Очищення зайвих пробілів
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    return clean_text


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Безпечно отримує значення з словника, підтримуючи вкладені ключі.

    Args:
        data: Словник для пошуку
        key: Ключ (може бути вкладеним, наприклад "user.profile.name")
        default: Значення за замовчуванням

    Returns:
        Знайдене значення або default
    """
    if not isinstance(data, dict):
        return default

    keys = key.split('.')
    current = data

    try:
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        return current
    except (KeyError, TypeError):
        return default


def generate_sku(name: str, length: int = 8) -> str:
    """
    Генерує SKU на основі назви товару.

    Args:
        name: Назва товару
        length: Довжина генерованої частини

    Returns:
        Згенерований SKU
    """
    if not name:
        return generate_random_string(length)

    # Беремо перші літери кожного слова
    words = name.split()
    prefix = ''.join([word[0].upper() for word in words if word])

    # Додаємо випадкові символи
    suffix = generate_random_string(length - len(prefix))

    return (prefix + suffix)[:length].upper()


def generate_random_string(length: int = 8,
                           include_digits: bool = True,
                           include_uppercase: bool = True,
                           include_lowercase: bool = True) -> str:
    """
    Генерує випадковий рядок.

    Args:
        length: Довжина рядка
        include_digits: Включати цифри
        include_uppercase: Включати великі літери
        include_lowercase: Включати малі літери

    Returns:
        Випадковий рядок
    """
    chars = ""
    if include_lowercase:
        chars += string.ascii_lowercase
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_digits:
        chars += string.digits

    if not chars:
        chars = string.ascii_letters + string.digits

    return ''.join(secrets.choice(chars) for _ in range(length))


def hash_string(text: str, algorithm: str = "sha256") -> str:
    """
    Хешує рядок.

    Args:
        text: Текст для хешування
        algorithm: Алгоритм хешування

    Returns:
        Хеш рядка
    """
    if not text:
        return ""

    hash_obj = hashlib.new(algorithm)
    hash_obj.update(text.encode('utf-8'))
    return hash_obj.hexdigest()


def build_url(base_url: str, path: str, **params) -> str:
    """
    Будує URL з базової адреси та параметрів.

    Args:
        base_url: Базова URL
        path: Шлях
        **params: GET параметри

    Returns:
        Повна URL
    """
    # Об'єднуємо базову URL з шляхом
    full_url = urljoin(base_url.rstrip('/') + '/', path.lstrip('/'))

    # Додаємо параметри
    if params:
        query_parts = []
        for key, value in params.items():
            if value is not None:
                query_parts.append(f"{key}={value}")

        if query_parts:
            separator = '&' if '?' in full_url else '?'
            full_url += separator + '&'.join(query_parts)

    return full_url


def is_valid_url(url: str) -> bool:
    """
    Перевіряє чи є URL валідною.

    Args:
        url: URL для перевірки

    Returns:
        True якщо URL валідна
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def chunk_list(lst: list, chunk_size: int):
    """
    Розбиває список на частини заданого розміру.

    Args:
        lst: Список для розбиття
        chunk_size: Розмір частини

    Yields:
        Частини списку
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def flatten_dict(data: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Вирівнює вкладений словник.

    Args:
        data: Словник для вирівнювання
        parent_key: Батьківський ключ
        sep: Роздільник

    Returns:
        Вирівняний словник
    """
    items = []
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep).items())
        else:
            items.append((new_key, value))

    return dict(items)


def get_current_timestamp() -> int:
    """
    Отримує поточний timestamp в UTC.

    Returns:
        Timestamp в секундах
    """
    return int(datetime.now(timezone.utc).timestamp())


def bytes_to_human_readable(size_bytes: int) -> str:
    """
    Конвертує байти у зручний для читання формат.

    Args:
        size_bytes: Розмір у байтах

    Returns:
        Відформатований розмір
    """
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f}{size_names[i]}"


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """
    Маскує чутливі дані, залишаючи видимими тільки частину.

    Args:
        data: Дані для маскування
        mask_char: Символ для маскування
        visible_chars: Кількість видимих символів з кінця

    Returns:
        Замасковані дані
    """
    if not data or len(data) <= visible_chars:
        return mask_char * len(data) if data else ""

    visible_part = data[-visible_chars:]
    masked_part = mask_char * (len(data) - visible_chars)

    return masked_part + visible_part