"""Утиліти безпеки для Magento Python бібліотеки."""

import hashlib
import hmac
import secrets
import base64
from typing import Optional, Union


class SecurityUtils:
    """Утиліти для безпеки та шифрування."""

    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """Згенерувати безпечний API ключ."""
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_secret(length: int = 64) -> str:
        """Згенерувати безпечний секрет."""
        return secrets.token_hex(length)

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Хешувати пароль з сіллю.

        Returns:
            tuple: (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)

        # Використовуємо PBKDF2 для безпечного хешування
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100k ітерацій
        )

        return base64.b64encode(hashed).decode('utf-8'), salt

    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """Перевірити пароль проти хешу."""
        expected_hash, _ = SecurityUtils.hash_password(password, salt)
        return hmac.compare_digest(expected_hash, hashed_password)

    @staticmethod
    def create_signature(
            data: Union[str, bytes],
            secret: str,
            algorithm: str = 'sha256'
    ) -> str:
        """Створити HMAC підпис для даних."""
        if isinstance(data, str):
            data = data.encode('utf-8')

        signature = hmac.new(
            secret.encode('utf-8'),
            data,
            getattr(hashlib, algorithm)
        )

        return base64.b64encode(signature.digest()).decode('utf-8')

    @staticmethod
    def verify_signature(
            data: Union[str, bytes],
            signature: str,
            secret: str,
            algorithm: str = 'sha256'
    ) -> bool:
        """Перевірити HMAC підпис."""
        expected_signature = SecurityUtils.create_signature(data, secret, algorithm)
        return hmac.compare_digest(signature, expected_signature)

    @staticmethod
    def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
        """Замаскувати чутливі дані для логування."""
        if len(data) <= visible_chars * 2:
            return '*' * len(data)

        return (
                data[:visible_chars] +
                '*' * (len(data) - visible_chars * 2) +
                data[-visible_chars:]
        )

    @staticmethod
    def is_secure_url(url: str) -> bool:
        """Перевірити, чи URL використовує HTTPS."""
        return url.lower().startswith('https://')

    @staticmethod
    def sanitize_header_value(value: str) -> str:
        """Очистити значення заголовка від небезпечних символів."""
        # Видаляємо символи, які можуть призвести до HTTP header injection
        dangerous_chars = ['\r', '\n', '\0']
        for char in dangerous_chars:
            value = value.replace(char, '')

        return value.strip()


class TokenValidator:
    """Валідатор для токенів доступу."""

    @staticmethod
    def is_valid_format(token: str) -> bool:
        """Перевірити формат токена Magento."""
        if not token or not isinstance(token, str):
            return False

        # Magento токени зазвичай мають певну довжину та формат
        # Базова перевірка довжини та символів
        if len(token) < 20 or len(token) > 255:
            return False

        # Перевіряємо, що токен містить лише допустимі символи
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.')
        return all(c in allowed_chars for c in token)

    @staticmethod
    def extract_token_info(token: str) -> dict:
        """Витягти інформацію з токена (якщо можливо)."""
        info = {
            'length': len(token) if token else 0,
            'format_valid': TokenValidator.is_valid_format(token),
            'masked_token': SecurityUtils.mask_sensitive_data(token) if token else None
        }

        return info


# Константи для безпеки
class SecurityConstants:
    """Константи безпеки."""

    # Мінімальні вимоги до паролів
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL_CHARS = True

    # Таймаути
    DEFAULT_TOKEN_TTL = 14400  # 4 години
    MAX_TOKEN_TTL = 86400  # 24 години

    # Ліміти
    MAX_RETRY_ATTEMPTS = 3
    RATE_LIMIT_WINDOW = 60  # секунд
    MAX_REQUESTS_PER_WINDOW = 100

    # Заголовки безпеки
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }