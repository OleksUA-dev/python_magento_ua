"""Експорт всіх базових компонентів."""

from .base_client import BaseClient
from .http_adapter import HttpAdapter
from .dependency_injection import (
    DIContainer,
    get_container,
    register,
    register_instance,
    resolve,
    service,
    inject,
)

__all__ = [
    "BaseClient",
    "HttpAdapter",
    "DIContainer",
    "get_container",
    "register",
    "register_instance",
    "resolve",
    "service",
    "inject",
]