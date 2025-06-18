#!/usr/bin/env python3
"""
Скрипт для тестування підключення до Magento API.
"""

import asyncio
import sys
import os
from pathlib import Path

# Додаємо шлях до проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from magento_ua.settings import Settings
    from magento_ua.client import MagentoClient, SyncMagentoClient
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    print("Переконайтеся що проект встановлено: pip install -e .")
    sys.exit(1)


def check_env_file():
    """Перевірити наявність .env файлу."""
    env_file = project_root / ".env"
    if not env_file.exists():
        print("❌ Файл .env не знайдено!")
        print("Створіть файл .env з налаштуваннями Magento API")
        print("Приклад:")
        print("MAGENTO_BASE_URL=http://localhost:8080")
        print("MAGENTO_USERNAME=your_api_user")
        print("MAGENTO_PASSWORD=your_api_password")
        return False

    print("✅ Файл .env знайдено")
    return True


def test_settings_loading():
    """Тестувати завантаження налаштувань."""
    print("\n🔧 Тестування завантаження налаштувань...")

    try:
        settings = Settings.from_env()
        print(f"✅ Налаштування завантажено:")
        print(f"   Base URL: {settings.base_url}")
        print(f"   Username: {settings.username}")
        print(f"   Verify SSL: {settings.verify_ssl}")
        print(f"   Timeout: {settings.timeout}")
        return settings
    except Exception as e:
        print(f"❌ Помилка завантаження налаштувань: {e}")
        return None


async def test_async_client(settings):
    """Тестувати асинхронний клієнт."""
    print("\n🔄 Тестування асинхронного клієнта...")

    try:
        async with MagentoClient(settings) as client:
            print("✅ Клієнт створено")

            # Тест health check
            health = await client.health_check()
            print(f"✅ Health check: {health['client']}")

            # Тест отримання токену
            headers = await client.get_auth_headers()
            print("✅ Токен отримано")

            # Тест API запиту - отримання інформації про магазин
            try:
                response = await client.http_adapter.get(
                    "rest/V1/store/storeConfigs",
                    headers=headers
                )
                print("✅ API запит успішний")
                print(f"   Store configs count: {len(response) if isinstance(response, list) else 'N/A'}")
                return True
            except Exception as e:
                print(f"⚠️  API запит не вдався: {e}")
                # Спробуємо простіший запит
                try:
                    response = await client.http_adapter.get(
                        "rest/V1/modules",
                        headers=headers
                    )
                    print("✅ Альтернативний API запит успішний")
                    return True
                except Exception as e2:
                    print(f"❌ Всі API запити не вдались: {e2}")
                    return False

    except Exception as e:
        print(f"❌ Помилка з асинхронним клієнтом: {e}")
        return False


def test_sync_client(settings):
    """Тестувати синхронний клієнт."""
    print("\n🔄 Тестування синхронного клієнта...")

    try:
        with SyncMagentoClient(settings) as client:
            print("✅ Синхронний клієнт створено")

            # Тест health check
            health = client.health_check()
            print(f"✅ Health check: {health['client']}")

            return True

    except Exception as e:
        print(f"❌ Помилка з синхронним клієнтом: {e}")
        return False


def test_direct_api_call(settings):
    """Тестувати пряме звернення до API."""
    print("\n🌐 Тестування прямого API виклику...")

    import httpx

    try:
        # Спробуємо отримати токен
        token_url = f"{settings.base_url}/rest/V1/integration/admin/token"
        auth_data = {
            "username": settings.username,
            "password": settings.password
        }

        with httpx.Client(verify=settings.verify_ssl, timeout=settings.timeout) as client:
            response = client.post(token_url, json=auth_data)

            if response.status_code == 200:
                token = response.json().strip('"')
                print("✅ Токен отримано через прямий API виклик")

                # Спробуємо зробити запит з токеном
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }

                test_url = f"{settings.base_url}/rest/V1/store/storeConfigs"
                test_response = client.get(test_url, headers=headers)

                if test_response.status_code == 200:
                    print("✅ API запит з токеном успішний")
                    data = test_response.json()
                    print(f"   Отримано store configs: {len(data) if isinstance(data, list) else 'N/A'}")
                    return True
                else:
                    print(f"⚠️  API запит повернув статус {test_response.status_code}")
                    print(f"   Відповідь: {test_response.text[:200]}...")
                    return False
            else:
                print(f"❌ Не вдалося отримати токен. Статус: {response.status_code}")
                print(f"   Відповідь: {response.text[:200]}...")
                return False

    except Exception as e:
        print(f"❌ Помилка прямого API виклику: {e}")
        return False


def print_troubleshooting():
    """Вивести поради по усуненню проблем."""
    print("\n🔧 Поради по усуненню проблем:")
    print("\n1. Перевірте що Magento запущено:")
    print("   docker ps")
    print("   curl http://localhost:8080")

    print("\n2. Перевірте API користувача в Magento Admin:")
    print("   System → Extensions → Integrations")
    print("   Або System → Permissions → All Users")

    print("\n3. Перевірте налаштування в .env файлі:")
    print("   MAGENTO_BASE_URL має відповідати вашій Magento")
    print("   MAGENTO_USERNAME/PASSWORD мають бути валідні")

    print("\n4. Для локальної розробки:")
    print("   MAGENTO_VERIFY_SSL=false")
    print("   MAGENTO_TIMEOUT=30")

    print("\n5. Увімкніть детальне логування:")
    print("   MAGENTO_LOG_LEVEL=DEBUG")
    print("   MAGENTO_ENABLE_REQUEST_LOGGING=true")


async def main():
    """Головна функція."""
    print("🚀 Тестування підключення до Magento API")
    print("=" * 50)

    # Перевірка .env файлу
    if not check_env_file():
        return 1

    # Завантаження налаштувань
    settings = test_settings_loading()
    if not settings:
        return 1

    # Тестування прямого API виклику
    direct_api_success = test_direct_api_call(settings)

    if direct_api_success:
        print("\n✅ Пряме API підключення працює!")

        # Тестування наших клієнтів
        async_success = await test_async_client(settings)
        sync_success = test_sync_client(settings)

        if async_success and sync_success:
            print("\n🎉 Всі тести пройшли успішно!")
            print("Ваш Magento API готовий до використання з Python клієнтом.")
            return 0
        else:
            print("\n⚠️  Деякі тести не пройшли, але базове підключення працює.")
            return 0
    else:
        print("\n❌ Базове API підключення не працює.")
        print_troubleshooting()
        return 1


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n⏹️  Тестування перервано користувачем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Неочікувана помилка: {e}")
        sys.exit(1)