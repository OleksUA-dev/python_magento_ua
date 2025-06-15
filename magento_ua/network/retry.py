"""Стратегії повторення запитів."""

import asyncio
import random
import time
from abc import ABC, abstractmethod
from typing import List, Type, Union, Callable, Any
from dataclasses import dataclass


@dataclass
class RetryStrategy(ABC):
    """Базова стратегія повторення."""

    max_attempts: int = 3
    retryable_exceptions: List[Type[Exception]] = None

    def __post_init__(self):
        """Ініціалізація після створення."""
        if self.retryable_exceptions is None:
            self.retryable_exceptions = [Exception]

    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """Отримати затримку для спроби."""
        pass

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Перевірити чи потрібно повторювати."""
        if attempt >= self.max_attempts:
            return False

        return any(
            isinstance(exception, exc_type)
            for exc_type in self.retryable_exceptions
        )

    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """Виконати функцію з повтореннями (async)."""
        last_exception = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if not self.should_retry(e, attempt):
                    raise

                if attempt < self.max_attempts:
                    delay = self.get_delay(attempt)
                    await asyncio.sleep(delay)

        # Якщо всі спроби вичерпано
        raise last_exception

    def execute_sync(self, func: Callable, *args, **kwargs) -> Any:
        """Виконати функцію з повтореннями (sync)."""
        last_exception = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if not self.should_retry(e, attempt):
                    raise

                if attempt < self.max_attempts:
                    delay = self.get_delay(attempt)
                    time.sleep(delay)

        # Якщо всі спроби вичерпано
        raise last_exception


@dataclass
class ExponentialBackoff(RetryStrategy):
    """Експоненційна затримка."""

    base_delay: float = 1.0  # Базова затримка в секундах
    max_delay: float = 60.0  # Максимальна затримка
    multiplier: float = 2.0  # Множник для експоненціального зростання
    jitter: bool = True  # Додати випадковість

    def get_delay(self, attempt: int) -> float:
        """Обчислити затримку для спроби."""
        # Експоненційна затримка
        delay = self.base_delay * (self.multiplier ** (attempt - 1))

        # Обмежити максимальною затримкою
        delay = min(delay, self.max_delay)

        # Додати jitter для запобігання thundering herd
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)

        return delay


@dataclass
class LinearBackoff(RetryStrategy):
    """Лінійна затримка."""

    base_delay: float = 1.0  # Базова затримка
    increment: float = 1.0  # Приріст затримки
    max_delay: float = 10.0  # Максимальна затримка

    def get_delay(self, attempt: int) -> float:
        """Обчислити затримку для спроби."""
        delay = self.base_delay + (self.increment * (attempt - 1))
        return min(delay, self.max_delay)


@dataclass
class FixedDelay(RetryStrategy):
    """Фіксована затримка."""

    delay: float = 1.0  # Фіксована затримка

    def get_delay(self, attempt: int) -> float:
        """Повернути фіксовану затримку."""
        return self.delay


# Декоратор для автоматичного повторення
def retry(
        strategy: RetryStrategy = None,
        max_attempts: int = 3,
        delay: Union[float, RetryStrategy] = 1.0,
        exceptions: List[Type[Exception]] = None
):
    """
    Декоратор для автоматичного повторення функцій.

    Args:
        strategy: Стратегія повторення
        max_attempts: Максимальна кількість спроб
        delay: Затримка між спробами або стратегія
        exceptions: Винятки для повторення
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Створити стратегію якщо не передана
            if strategy is None:
                if isinstance(delay, (int, float)):
                    retry_strategy = FixedDelay(
                        delay=delay,
                        max_attempts=max_attempts,
                        retryable_exceptions=exceptions
                    )
                else:
                    retry_strategy = delay
            else:
                retry_strategy = strategy

            # Виконати з повтореннями
            if asyncio.iscoroutinefunction(func):
                return retry_strategy.execute_async(func, *args, **kwargs)
            else:
                return retry_strategy.execute_sync(func, *args, **kwargs)

        return wrapper

    return decorator
