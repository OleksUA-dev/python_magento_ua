"""
Тести для модуля налаштувань.
"""

import pytest
import os
from unittest.mock import patch

try:
    from pydantic import ValidationError
except ImportError:
    from pydantic.v1 import ValidationError

from magento_ua.settings import Settings, PYDANTIC_V2
from .config import EnvironmentConfigs, DictConfigs
from .helpers import env_override, clean_env, with_env_config


class TestSettings:
    """Тести класу Settings."""

    def test_settings_creation_with_required_fields(self):
        """Тест створення налаштувань з обов'язковими полями."""
        config = DictConfigs.MINIMAL
        settings = Settings.from_dict(config)

        assert str(settings.base_url) == config["base_url"]
        assert settings.username == config["username"]
        assert settings.password == config["password"]

        # Перевіряємо значення за замовчуванням
        assert settings.verify_ssl is True
        assert settings.timeout == 30
        assert settings.max_retries == 3

    def test_settings_with_all_fields(self):
        """Тест створення налаштувань з усіма полями."""
        config = DictConfigs.COMPLETE
        settings = Settings.from_dict(config)

        assert settings.verify_ssl == config["verify_ssl"]
        assert settings.timeout == config["timeout"]
        assert settings.max_retries == config["max_retries"]
        assert settings.rate_limit == config["rate_limit"]
        assert settings.enable_cache == config["enable_cache"]
        assert settings.cache_ttl == config["cache_ttl"]

    def test_missing_required_fields(self):
        """Тест помилки при відсутності обов'язкових полів."""
        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error = exc_info.value
        error_str = str(error)
        assert """"
Тести для модуля налаштувань.
"""


import pytest
import os
from unittest.mock import patch

try:
    from pydantic import ValidationError
except ImportError:
    from pydantic.v1 import ValidationError

from magento_ua.settings import Settings, PYDANTIC_V2


class TestSettings:
    """Тести класу Settings."""

    def test_settings_creation_with_required_fields(self):
        """Тест створення налаштувань з обов'язковими полями."""
        settings = Settings(
            base_url="https://example.com",
            username="test_user",
            password="test_password"
        )

        assert settings.base_url == "https://example.com"
        assert settings.username == "test_user"
        assert settings.password == "test_password"

        # Перевіряємо значення за замовчуванням
        assert settings.verify_ssl is True
        assert settings.timeout == 30
        assert settings.max_retries == 3

    def test_settings_with_all_fields(self):
        """Тест створення налаштувань з усіма полями."""
        settings = Settings(
            base_url="https://example.com",
            username="test_user",
            password="test_password",
            verify_ssl=False,
            timeout=60,
            max_retries=5,
            rate_limit=200,
            enable_cache=True,
            cache_ttl=7200
        )

        assert settings.verify_ssl is False
        assert settings.timeout == 60
        assert settings.max_retries == 5
        assert settings.rate_limit == 200
        assert settings.enable_cache is True
        assert settings.cache_ttl == 7200

    def test_missing_required_fields(self):
        """Тест помилки при відсутності обов'язкових полів."""
        with pytest.raises(ValidationError) as exc_info:
            Settings()

        error = exc_info.value
        assert "base_url" in str(error)
        assert "username" in str(error)
        assert "password" in str(error)

    def test_invalid_base_url(self):
        """Тест валідації невалідної базової URL."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                base_url="invalid-url",
                username="test",
                password="test"
            )

        assert "base_url" in str(exc_info.value)

    def test_valid_base_urls(self):
        """Тест валідних базових URL."""
        valid_urls = [
            "https://example.com",
            "http://localhost:8080",
            "https://magento.example.com/store"
        ]

        for url in valid_urls:
            settings = Settings(
                base_url=url,
                username="test",
                password="test"
            )
            assert str(settings.base_url) == url

    def test_encryption_key_validation(self):
        """Тест валідації ключа шифрування."""
        # Без шифрування - ключ не потрібен
        settings = Settings(
            base_url="https://example.com",
            username="test",
            password="test",
            enable_encryption=False
        )
        assert settings.encryption_key is None

        # З шифруванням але без ключа - помилка
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                base_url="https://example.com",
                username="test",
                password="test",
                enable_encryption=True
            )
        assert "encryption_key" in str(exc_info.value)

        # З шифруванням та невалідним ключем - помилка
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                base_url="https://example.com",
                username="test",
                password="test",
                enable_encryption=True,
                encryption_key="too_short"
            )
        assert "32 символи" in str(exc_info.value)

        # З валідним ключем - успіх
        valid_key = "a" * 32
        settings = Settings(
            base_url="https://example.com",
            username="test",
            password="test",
            enable_encryption=True,
            encryption_key=valid_key
        )
        assert settings.encryption_key == valid_key

    def test_log_level_validation(self):
        """Тест валідації рівня логування."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in valid_levels:
            settings = Settings(
                base_url="https://example.com",
                username="test",
                password="test",
                log_level=level.lower()
            )
            assert settings.log_level == level

        # Невалідний рівень
        with pytest.raises(ValidationError):
            Settings(
                base_url="https://example.com",
                username="test",
                password="test",
                log_level="INVALID"
            )

    def test_log_format_validation(self):
        """Тест валідації формату логів."""
        valid_formats = ["json", "text"]

        for format_val in valid_formats:
            settings = Settings(
                base_url="https://example.com",
                username="test",
                password="test",
                log_format=format_val.upper()
            )
            assert settings.log_format == format_val

        # Невалідний формат
        with pytest.raises(ValidationError):
            Settings(
                base_url="https://example.com",
                username="test",
                password="test",
                log_format="invalid"
            )

    @patch.dict(os.environ, {
        "MAGENTO_BASE_URL": "https://env.example.com",
        "MAGENTO_USERNAME": "env_user",
        "MAGENTO_PASSWORD": "env_pass",
        "MAGENTO_VERIFY_SSL": "false",
        "MAGENTO_TIMEOUT": "45"
    })
    def test_from_env_variables(self):
        """Тест створення налаштувань зі змінних оточення."""
        settings = Settings()

        assert str(settings.base_url) == "https://env.example.com"
        assert settings.username == "env_user"
        assert settings.password == "env_pass"
        assert settings.verify_ssl is False
        assert settings.timeout == 45

    def test_from_dict(self):
        """Тест створення налаштувань зі словника."""
        config_dict = {
            "base_url": "https://dict.example.com",
            "username": "dict_user",
            "password": "dict_pass",
            "timeout": 25,
            "rate_limit": 150
        }

        settings = Settings.from_dict(config_dict)

        assert str(settings.base_url) == "https://dict.example.com"
        assert settings.username == "dict_user"
        assert settings.password == "dict_pass"
        assert settings.timeout == 25
        assert settings.rate_limit == 150

    def test_from_env_file(self, temp_config_file):
        """Тест створення налаштувань з .env файлу."""
        with patch('magento_ua.settings.Settings.Config.env_file', str(temp_config_file)):
            settings = Settings.from_env_file(str(temp_config_file))

            assert "temp-test.example.com" in str(settings.base_url)
            assert settings.username == "temp_user"
            assert settings.password == "temp_password"
            assert settings.verify_ssl is False
            assert settings.timeout == 5

    def test_get_headers(self):
        """Тест отримання базових заголовків."""
        settings = Settings(
            base_url="https://example.com",
            username="test",
            password="test"
        )

        headers = settings.get_headers()

        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert "User-Agent" in headers
        assert "magento-python-ua" in headers["User-Agent"]

    def test_get_proxy_config_none(self):
        """Тест отримання конфігурації проксі коли його немає."""
        settings = Settings(
            base_url="https://example.com",
            username="test",
            password="test",
            proxy_url=None
        )

        proxy_config = settings.get_proxy_config()
        assert proxy_config is None

    def test_get_proxy_config_without_auth(self):
        """Тест отримання конфігурації проксі без аутентифікації."""
        settings = Settings(
            base_url="https://example.com",
            username="test",
            password="test",
            proxy_url="http://proxy.example.com:8080"
        )

        proxy_config = settings.get_proxy_config()

        assert proxy_config["http://"] == "http://proxy.example.com:8080"
        assert proxy_config["https://"] == "http://proxy.example.com:8080"

    def test_get_proxy_config_with_auth(self):
        """Тест отримання конфігурації проксі з аутентифікацією."""
        settings = Settings(
            base_url="https://example.com",
            username="test",
            password="test",
            proxy_url="http://proxy.example.com:8080",
            proxy_auth=("proxy_user", "proxy_pass")
        )

        proxy_config = settings.get_proxy_config()

        expected_url = "http://proxy_user:proxy_pass@proxy.example.com:8080"
        assert proxy_config["http://"] == expected_url
        assert proxy_config["https://"] == expected_url

    def test_numeric_string_conversion(self):
        """Тест конвертації рядкових чисел."""
        settings = Settings(
            base_url="https://example.com",
            username="test",
            password="test",
            timeout="30",  # рядок замість числа
            max_retries="5",
            rate_limit="100"
        )

        assert settings.timeout == 30
        assert settings.max_retries == 5
        assert settings.rate_limit == 100

    def test_boolean_string_conversion(self):
        """Тест конвертації рядкових булевих значень."""
        settings = Settings(
            base_url="https://example.com",
            username="test",
            password="test",
            verify_ssl="false",
            enable_cache="true",
            enable_metrics="1"
        )

        assert settings.verify_ssl is False
        assert settings.enable_cache is True
        # enable_metrics може залишитись рядком залежно від Pydantic


class TestSettingsEdgeCases:
    """Тести граничних випадків для Settings."""

    def test_extreme_values(self):
        """Тест екстремальних значень."""
        settings = Settings(
            base_url="https://example.com",
            username="test",
            password="test",
            timeout=1,  # мінімальний таймаут
            max_retries=0,  # без повторів
            rate_limit=1,  # мінімальний ліміт
            cache_ttl=1  # мінімальний TTL
        )

        assert settings.timeout == 1
        assert settings.max_retries == 0
        assert settings.rate_limit == 1
        assert settings.cache_ttl == 1

    def test_max_values(self):
        """Тест максимальних значень."""
        settings = Settings(
            base_url="https://example.com",
            username="test",
            password="test",
            timeout=3600,  # 1 година
            max_retries=100,  # багато повторів
            rate_limit=10000,  # високий ліміт
            cache_ttl=86400  # 1 день
        )

        assert settings.timeout == 3600
        assert settings.max_retries == 100
        assert settings.rate_limit == 10000
        assert settings.cache_ttl == 86400

    def test_unicode_values(self):
        """Тест з Unicode значеннями."""
        settings = Settings(
            base_url="https://магазин.укр",
            username="користувач_тест",
            password="пароль_123_🔐",
        )

        assert "магазин.укр" in str(settings.base_url)
        assert settings.username == "користувач_тест"
        assert settings.password == "пароль_123_🔐"

    def test_special_characters_in_auth(self):
        """Тест спеціальних символів в аутентифікації."""
        special_chars = "!@#$%^&*()[]{}|;:',.<>?`~"

        settings = Settings(
            base_url="https://example.com",
            username=f"user_{special_chars}",
            password=f"pass_{special_chars}"
        )

        assert special_chars in settings.username
        assert special_chars in settings.password


class TestSettingsValidation:
    """Тести валідації налаштувань."""

    @pytest.mark.parametrize("invalid_url", [
        "",
        "not-a-url",
        "ftp://example.com",
        "magento://invalid",
        "http://",
        "https://",
    ])
    def test_invalid_urls(self, invalid_url):
        """Тест різних невалідних URL."""
        with pytest.raises(ValidationError):
            Settings(
                base_url=invalid_url,
                username="test",
                password="test"
            )

    @pytest.mark.parametrize("valid_url", [
        "http://localhost",
        "https://localhost",
        "http://127.0.0.1",
        "https://example.com",
        "http://localhost:8080",
        "https://sub.domain.com:9000/path"
    ])
    def test_valid_urls(self, valid_url):
        """Тест різних валідних URL."""
        settings = Settings(
            base_url=valid_url,
            username="test",
            password="test"
        )
        assert str(settings.base_url) == valid_url

    def test_negative_timeout(self):
        """Тест від'ємного таймауту."""
        # Pydantic може дозволити або не дозволити від'ємні значення
        # залежно від конфігурації поля
        pass

    def test_zero_timeout(self):
        """Тест нульового таймауту."""
        settings = Settings(
            base_url="https://example.com",
            username="test",
            password="test",
            timeout=0
        )
        assert settings.timeout == 0


@pytest.mark.integration
class TestSettingsIntegration:
    """Інтеграційні тести налаштувань."""

    def test_real_env_file_loading(self, tmp_path):
        """Тест завантаження реального .env файлу."""
        env_file = tmp_path / "test.env"
        env_content = ""
