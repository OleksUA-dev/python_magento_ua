"""Простий Dependency Injection контейнер."""

import inspect
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

T = TypeVar('T')


class DIContainer:
    """Простий контейнер для Dependency Injection."""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._instances: Dict[str, Any] = {}

    def register(
            self,
            name: str,
            factory: Union[Type, Callable],
            singleton: bool = False
    ) -> None:
        """Зареєструвати сервіс в контейнері.

        Args:
            name: Назва сервісу
            factory: Клас або фабрична функція для створення сервісу
            singleton: Чи створювати один екземпляр (singleton pattern)
        """
        self._factories[name] = factory
        if singleton:
            self._singletons[name] = True

    def register_instance(self, name: str, instance: Any) -> None:
        """Зареєструвати готовий екземпляр."""
        self._instances[name] = instance

    def resolve(self, name: Union[str, Type[T]]) -> T:
        """Отримати сервіс з контейнера.

        Args:
            name: Назва сервісу або тип класу

        Returns:
            Екземпляр сервісу
        """
        # Якщо передано тип класу, використовуємо його назву
        if inspect.isclass(name):
            service_name = name.__name__
            service_type = name
        else:
            service_name = name
            service_type = None

        # Перевіряємо готові екземпляри
        if service_name in self._instances:
            return self._instances[service_name]

        # Перевіряємо singleton cache
        if service_name in self._singletons and service_name in self._services:
            return self._services[service_name]

        # Створюємо новий екземпляр
        if service_name in self._factories:
            factory = self._factories[service_name]
        elif service_type:
            factory = service_type
        else:
            raise ValueError(f"Service '{service_name}' not registered")

        instance = self._create_instance(factory)

        # Зберігаємо singleton
        if service_name in self._singletons:
            self._services[service_name] = instance

        return instance

    def _create_instance(self, factory: Callable) -> Any:
        """Створити екземпляр з автоматичним вирішенням залежностей."""
        if not inspect.isclass(factory) and not inspect.isfunction(factory):
            # Якщо це вже готовий об'єкт
            return factory

        # Отримуємо параметри конструктора
        signature = inspect.signature(factory)
        kwargs = {}

        for param_name, param in signature.parameters.items():
            # Пропускаємо self та args/kwargs
            if param_name == 'self':
                continue
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue

            # Спробуємо вирішити залежність
            try:
                # Спочатку за назвою параметра
                dependency = self.resolve(param_name)
                kwargs[param_name] = dependency
            except ValueError:
                # Потім за типом анотації
                if param.annotation != param.empty:
                    try:
                        dependency = self.resolve(param.annotation)
                        kwargs[param_name] = dependency
                    except ValueError:
                        pass

                # Якщо є значення за замовчуванням, використовуємо його
                if param.default != param.empty:
                    continue
                else:
                    # Якщо параметр обов'язковий і не вдалося вирішити
                    if param_name not in kwargs:
                        raise ValueError(
                            f"Cannot resolve dependency '{param_name}' for '{factory.__name__}'"
                        )

        return factory(**kwargs)

    def has(self, name: str) -> bool:
        """Перевірити, чи зареєстровано сервіс."""
        return (
                name in self._factories or
                name in self._instances or
                name in self._services
        )

    def clear(self) -> None:
        """Очистити контейнер."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._instances.clear()


# Глобальний контейнер за замовчуванням
_default_container = DIContainer()


def get_container() -> DIContainer:
    """Отримати глобальний DI контейнер."""
    return _default_container


def register(
        name: str,
        factory: Union[Type, Callable],
        singleton: bool = False
) -> None:
    """Зареєструвати сервіс у глобальному контейнері."""
    _default_container.register(name, factory, singleton)


def register_instance(name: str, instance: Any) -> None:
    """Зареєструвати екземпляр у глобальному контейнері."""
    _default_container.register_instance(name, instance)


def resolve(name: Union[str, Type[T]]) -> T:
    """Отримати сервіс з глобального контейнера."""
    return _default_container.resolve(name)


# Декоратор для автоматичної реєстрації
def service(name: Optional[str] = None, singleton: bool = False):
    """Декоратор для автоматичної реєстрації сервісу.

    Args:
        name: Назва сервісу (за замовчуванням - назва класу)
        singleton: Чи реєструвати як singleton
    """

    def decorator(cls):
        service_name = name or cls.__name__
        register(service_name, cls, singleton=singleton)
        return cls

    return decorator


# Декоратор для inject залежностей
def inject(container: Optional[DIContainer] = None):
    """Декоратор для автоматичного inject залежностей у метод.

    Args:
        container: DI контейнер (за замовчуванням глобальний)
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            di_container = container or _default_container

            # Отримуємо параметри функції
            signature = inspect.signature(func)
            for param_name, param in signature.parameters.items():
                # Пропускаємо вже передані аргументи
                if param_name in kwargs:
                    continue

                # Пропускаємо self, args, kwargs
                if param_name == 'self':
                    continue
                if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                    continue

                # Спробуємо вирішити залежність
                try:
                    if param.annotation != param.empty:
                        dependency = di_container.resolve(param.annotation)
                        kwargs[param_name] = dependency
                    else:
                        dependency = di_container.resolve(param_name)
                        kwargs[param_name] = dependency
                except ValueError:
                    # Якщо не вдалося вирішити і немає значення за замовчуванням
                    if param.default == param.empty:
                        continue  # Пропускаємо, можливо буде передано пізніше

            return func(*args, **kwargs)

        return wrapper

    return decorator