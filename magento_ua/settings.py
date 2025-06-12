# magento_ua/settings.py
"""Система налаштувань для Magento клієнта."""

from typing import Optional, Dict, Any
from pathlib import Path
from pydantic import BaseSettings, Field, validator
from pydantic.networks import HttpUrl


class Settings(BaseSettings):
    """Налаштування Magento клієнта."""

    # Основні налаштування
    base_url: HttpUrl = Field(..., description="Базова URL Magento магазину")
    username: str = Field(..., description="Ім'я користувача API")
    password: str = Field(..., description="Пароль API")

    # Налаштування безпеки
    verify_ssl: bool = Field(True, description="Перевіряти SSL сертифікати")
    ca_bundle: Optional[Path] = Field(None, description="Шлях до CA bundle")
    client_cert: Optional[tuple] = Field(None, description="Клієнтський сертифікат (cert_path, key_path)")
    enable_encryption: bool = Field(False, description="Увімкнути шифрування токенів")
    encryption_key: Optional[str] = Field(None, description="Ключ для шифрування (32 символи)")

    # Мережеві налаштування
    timeout: int = Field(30, description="Таймаут запитів в секундах")
    max_retries: int = Field(3, description="Максимальна кількість повторних спроб")
    retry_delay: float = Field(1.0, description="Затримка між повторними спробами")
    max_connections: int = Field(100, description="Максимальна кількість з'єднань")
    max_keepalive_connections: int = Field(20, description="Максимальна кількість keepalive з'єднань")

    # Rate limiting
    rate_limit: int = Field(100, description="Ліміт запитів на хвилину")
    rate_limit_window: int = Field(60, description="Вікно для rate limiting в секундах")

    # Проксі
    proxy_url: Optional[str] = Field(None, description="URL проксі сервера")
    proxy_auth: Optional[tuple] = Field(None, description="Аутентифікація проксі (username, password)")

    # Кешування
    enable_cache: bool = Field(False, description="Увімкнути кешування")
    cache_ttl: int = Field(3600, description="TTL кешу в секундах")
    cache_max_size: int = Field(1000, description="Максимальний розмір кешу")

    # Логування
    log_level: str = Field("INFO", description="Рівень логування")
    log_format: str = Field("json", description="Формат логів (json/text)")
    enable_request_logging: bool = Field(False, description="Логувати HTTP запити")

    # Брокер подій (для майбутнього)
    event_broker: Optional[str] = Field(None, description="Тип брокера подій (memory/redis/rabbitmq)")
    redis_url: Optional[str] = Field(None, description="URL Redis сервера")
    rabbitmq_url: Optional[str] = Field(None, description="URL RabbitMQ сервера")

    # Метрики (для майбутнього)
    enable_metrics: bool = Field(False, description="Увімкнути збір метрик")
    metrics_port: int = Field(9090, description="Порт для метрик")

    # Circuit Breaker (для майбутнього)
    circuit_breaker_threshold: int = Field(5, description="Поріг спрацьовування circuit breaker")
    circuit_breaker_timeout: int = Field(60, description="Таймаут circuit breaker")

    class Config:
        env_prefix = "MAGENTO_"
        env_file = ".env"
        case_sensitive = False

    @validator("encryption_key")
    def validate_encryption_key(cls, v, values):
        """Валідація ключа шифрування."""
        if values.get("enable_encryption") and not v:
            raise ValueError("encryption_key обов'язковий коли enable_encryption=True")
        if v and len(v) != 32:
            raise ValueError("encryption_key повинен бути довжиною 32 символи")
        return v

    @validator("base_url")
    def validate_base_url(cls, v):
        """Валідація базової URL."""
        if not str(v).startswith(("http://", "https://")):
            raise ValueError("base_url повинна починатись з http:// або https://")
        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        """Валідація рівня логування."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level повинен бути одним з: {valid_levels}")
        return v.upper()

    @validator("log_format")
    def validate_log_format(cls, v):
        """Валідація формату логів."""
        valid_formats = ["json", "text"]
        if v.lower() not in valid_formats:
            raise ValueError(f"log_format повинен бути одним з: {valid_formats}")
        return v.lower()

    def get_headers(self) -> Dict[str, str]:
        """Отримати базові заголовки для запитів."""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "magento-python-ua/0.1.0"
        }

    def get_proxy_config(self) -> Optional[Dict[str, Any]]:
        """Отримати конфігурацію проксі."""
        if not self.proxy_url:
            return None

        config = {"http://": self.proxy_url, "https://": self.proxy_url}

        if self.proxy_auth:
            # Додати аутентифікацію до URL
            username, password = self.proxy_auth
            proxy_with_auth = self.proxy_url.replace("://", f"://{username}:{password}@")
            config = {"http://": proxy_with_auth, "https://": proxy_with_auth}

        return config

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Settings":
        """Створити Settings з словника."""
        return cls(**data)

    @classmethod
    def from_env_file(cls, env_file: str = ".env") -> "Settings":
        """Створити Settings з env файлу."""
        return cls(_env_file=env_file)