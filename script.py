#!/usr/bin/env python3
"""Скрипт для створення структури проекту magento-python-ua."""

import os
from pathlib import Path


def create_structure():
    """Створити структуру проекту."""

    # Список всіх файлів та папок
    files_and_dirs = [
        # Основні файли
        "magento_ua/__init__.py",
        "magento_ua/client.py",
        "magento_ua/settings.py",

        # Core
        "magento_ua/core/__init__.py",
        "magento_ua/core/base_client.py",
        "magento_ua/core/http_adapter.py",
        "magento_ua/core/dependency_injection.py",

        # Auth
        "magento_ua/auth/__init__.py",
        "magento_ua/auth/token_provider.py",
        "magento_ua/auth/security.py",

        # Network
        "magento_ua/network/__init__.py",
        "magento_ua/network/retry.py",
        "magento_ua/network/rate_limiter.py",

        # Exceptions
        "magento_ua/exceptions/__init__.py",
        "magento_ua/exceptions/base.py",
        "magento_ua/exceptions/api.py",
        "magento_ua/exceptions/network.py",

        # Models
        "magento_ua/models/__init__.py",
        "magento_ua/models/product.py",
        "magento_ua/models/order.py",
        "magento_ua/models/customer.py",

        # Endpoints
        "magento_ua/endpoints/__init__.py",
        "magento_ua/endpoints/base.py",
        "magento_ua/endpoints/products.py",
        "magento_ua/endpoints/orders.py",

        # Utils
        "magento_ua/utils/__init__.py",
        "magento_ua/utils/validation.py",
        "magento_ua/utils/helpers.py",

        # Tests
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/unit/__init__.py",
        "tests/integration/__init__.py",
        "tests/fixtures/__init__.py",

        # Examples
        "examples/basic_usage.py",
        "examples/async_operations.py",
        "examples/bulk_operations.py",

        # Docs
        "docs/installation.md",
        "docs/quickstart.md",
        "docs/configuration.md",

        # Root files
        "pyproject.toml",
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        ".env.example",
        ".gitignore"
    ]

    print("🚀 Створення структури проекту magento-python-ua...")

    for file_path in files_and_dirs:
        path = Path(file_path)

        # Створити папку якщо не існує
        path.parent.mkdir(parents=True, exist_ok=True)

        # Створити файл якщо не існує
        if not path.exists():
            path.touch()
            print(f"✅ Створено: {file_path}")
        else:
            print(f"⚠️  Вже існує: {file_path}")

    print("\n🎉 Структура проекту успішно створена!")
    print("Тепер можете почати копіювати код у відповідні файли.")


if __name__ == "__main__":
    create_structure()