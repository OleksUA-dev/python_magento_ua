"""Обмежувач швидкості запитів."""

import asyncio
import time
from typing import Optional
from dataclasses import dataclass


@dataclass
class TokenBucket:
    """Алгоритм Token Bucket для обмеження швидкості."""

    capacity: int  # Максимальна кількість токенів
    refill_rate: float  # Токенів на секунду
    tokens: float = 0  # Поточна кількість токенів
    last_refill: float = 0  # Час останнього поповнення

    def __post_init__(self):
        """Ініціалізація після створення."""
        self.tokens = self.capacity
        self.last_refill = time.time()

    def _refill(self) -> None:
        """Поповнити токени."""
        now = time.time()
        elapsed = now - self.last_refill

        # Додати токени на основі часу, що минув
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """Спробувати споживати токени."""
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def wait_time(self, tokens: int = 1) -> float:
        """Час очікування для отримання токенів."""
        self._refill()

        if self.tokens >= tokens:
            return 0

        needed_tokens = tokens - self.tokens
        return needed_tokens / self.refill_rate


class RateLimiter:
    """Обмежувач швидкості запитів."""

    def __init__(
            self,
            requests_per_minute: int = 60,
            burst_size: Optional[int] = None
    ):
        """
        Ініціалізація обмежувача.

        Args:
            requests_per_minute: Кількість запитів на хвилину
            burst_size: Максимальний розмір сплеску (за замовчуванням = requests_per_minute)
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size or requests_per_minute

        # Конвертувати в запити на секунду
        refill_rate = requests_per_minute / 60.0

        self.bucket = TokenBucket(
            capacity=self.burst_size,
            refill_rate=refill_rate
        )

        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> None:
        """Отримати дозвіл на виконання запиту."""
        async with self._lock:
            while not self.bucket.consume(tokens):
                wait_time = self.bucket.wait_time(tokens)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)

    def acquire_sync(self, tokens: int = 1) -> None:
        """Синхронна версія acquire."""
        while not self.bucket.consume(tokens):
            wait_time = self.bucket.wait_time(tokens)
            if wait_time > 0:
                time.sleep(wait_time)

    def available_tokens(self) -> int:
        """Кількість наявних токенів."""
        self.bucket._refill()
        return int(self.bucket.tokens)

    async def __aenter__(self):
        """Async context manager."""
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager cleanup."""
        pass

    def __enter__(self):
        """Sync context manager."""
        self.acquire_sync()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager cleanup."""
        pass