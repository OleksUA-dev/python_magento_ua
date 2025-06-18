"""Система налаштувань для Magento клієнта."""

from typing import Optional, Dict, Any, Tuple
from pathlib import Path

try:
    # Pydantic v2
    from pydantic import BaseModel, Field, field_validator, ConfigDict
    from pydantic import HttpUrl

    PYDANTIC_V2 = True
except ImportError:
    try:
        # Pydantic v1 fallback
        from pydantic import BaseSettings as BaseModel, Field, validator as field_validator
        from pydantic.networks import HttpUrl

        PYDANTIC_V2 = False
    except ImportError:
        raise ImportError("Pydantic не встановлено. Встановіть: pip install pydantic")


class Settings(BaseModel):
    """Налаштування Magento клієнта."""

    # Основні налаштування
    base_url: HttpUrl = Field(..., description="Базова URL Magento магазину")
    username: str = Field(..., description="Ім'я користувача API")
    password: str = Field(..., description="Пароль API")

    # Налаштування безпеки
    verify_ssl: bool = Field(True, description="Перевіряти SSL сертифікати")
    ca_bundle: Optional[Path] = Field(None, description="Шлях до CA bundle")
    client_cert: Optional[Tuple[str, str]] = Field(None, description="Клієнтський сертифікат (cert_path, key_path)")
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
    proxy_auth: Optional[Tuple[str, str]] = Field(None, description="Аутентифікація проксі (username, password)")

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

    if PYDANTIC_V2:
        model_config = ConfigDict(
            env_prefix="MAGENTO_",
            env_file=".env",
            case_sensitive=False,
            extra="forbid"
        )
    else:
        class Config:
            env_prefix = "MAGENTO_"
            env_file = ".env"
            case_sensitive = False

    # Валідатори
    if PYDANTIC_V2:
        @field_validator("encryption_key")
        @classmethod
        def validate_encryption_key(cls, v: Optional[str], info) -> Optional[str]:
            """Валідація ключа шифрування."""
            values = info.data if hasattr(info, 'data') else {}
            if values.get("enable_encryption") and not v:
                raise ValueError("encryption_key обов'язковий коли enable_encryption=True")
            if v and len(v) != 32:
                raise ValueError("encryption_key повинен бути довжиною 32 символи")
            return v

        @field_validator("base_url")
        @classmethod
        def validate_base_url(cls, v: HttpUrl) -> HttpUrl:
            """Валідація базової URL."""
            url_str = str(v)
            if not url_str.startswith(("http://", "https://")):
                raise ValueError("base_url повинна починатись з http:// або https://")
            return v

        @field_validator("log_level")
        @classmethod
        def validate_log_level(cls, v: str) -> str:
            """Валідація рівня логування."""
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if v.upper() not in valid_levels:
                raise ValueError(f"log_level повинен бути одним з: {valid_levels}")
            return v.upper()

        @field_validator("log_format")
        @classmethod
        def validate_log_format(cls, v: str) -> str:
            """Валідація формату логів."""
            valid_formats = ["json", "text"]
            if v.lower() not in valid_formats:
                raise ValueError(f"log_format повинен бути одним з: {valid_formats}")
            return v.lower()
    else:
        # Pydantic v1 валідатори
        @field_validator("encryption_key")
        def validate_encryption_key(cls, v, values):
            """Валідація ключа шифрування."""
            if values.get("enable_encryption") and not v:
                raise ValueError("encryption_key обов'язковий коли enable_encryption=True")
            if v and len(v) != 32:
                raise ValueError("encryption_key повинен бути довжиною 32 символи")
            return v

        @field_validator("base_url")
        def validate_base_url(cls, v):
            """Валідація базової URL."""
            if not str(v).startswith(("http://", "https://")):
                raise ValueError("base_url повинна починатись з http:// або https://")
            return v

        @field_validator("log_level")
        def validate_log_level(cls, v):
            """Валідація рівня логування."""
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if v.upper() not in valid_levels:
                raise ValueError(f"log_level повинен бути одним з: {valid_levels}")
            return v.upper()

        @field_validator("log_format")
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
            "User-Agent": "magento-python-ua/1.0.0"
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
        import os

        # Для Pydantic v2 потрібно вручну завантажити .env файл
        if PYDANTIC_V2:
            try:
                from dotenv import load_dotenv
                load_dotenv(env_file)
            except ImportError:
                # Якщо python-dotenv не встановлено, намагаємося вручну
                if os.path.exists(env_file):
                    with open(env_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                os.environ[key.strip()] = value.strip()

            # Читаємо змінні оточення з префіксом
            env_vars = {}
            prefix = "MAGENTO_"
            for key, value in os.environ.items():
                if key.startswith(prefix):
                    field_name = key[len(prefix):].lower()
                    env_vars[field_name] = value

            return cls(**env_vars)
        else:
            # Pydantic v1
            return cls(_env_file=env_file)

    @classmethod
    def from_env(cls) -> "Settings":
        """Створити Settings зі змінних оточення."""
        return cls.from_env_file()

    def model_dump_json(self, **kwargs) -> str:
        """Серіалізація в JSON (Pydantic v2 compatible)."""
        if PYDANTIC_V2:
            return super().model_dump_json(**kwargs)
        else:
            return self.json(**kwargs)

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Серіалізація в dict (Pydantic v2 compatible)."""
        if PYDANTIC_V2:
            return super().model_dump(**kwargs)
        else:
            return self.dict(**kwargs)


# Для зворотної сумісності
def create_settings(**kwargs) -> Settings:
    """Фабрична функція для створення налаштувань."""
    return Settings(**kwargs)


def load_settings_from_env(env_file: str = ".env") -> Settings:
    """Завантажити налаштування з .env файлу."""
    return Settings.from_env_file(env_file)


# Експорт для зручності
__all__ = [
    "Settings",
    "create_settings",
    "load_settings_from_env",
    "PYDANTIC_V2"
]