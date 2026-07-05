"""infrastructure/common/cache.py — Cache TTL simple, en memoria, async-safe.

No pretende ser Redis: vive en memoria del proceso y se pierde al reiniciar.
Es suficiente para evitar llamadas repetidas a APIs externas (Gemini, Yahoo
Finance) dentro de una ventana corta de segundos — la mayoría de requests al
dashboard piden lo mismo varias veces por minuto.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass
class _Entry(Generic[T]):
    value: T
    expires_at: float


class TTLCache(Generic[T]):
    """Cache clave → valor con expiración por tiempo, protegida con un lock."""

    def __init__(self, ttl_seconds: float, max_size: int = 256) -> None:
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._store: dict[str, _Entry[T]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[T]:
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if entry.expires_at < time.monotonic():
                del self._store[key]
                return None
            return entry.value

    async def set(self, key: str, value: T) -> None:
        async with self._lock:
            if len(self._store) >= self._max_size and key not in self._store:
                # FIFO simple, no es un LRU real — suficiente para este tamaño de cache
                oldest_key = next(iter(self._store))
                del self._store[oldest_key]
            self._store[key] = _Entry(value=value, expires_at=time.monotonic() + self._ttl)

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()

    def stats(self) -> dict:
        return {
            "size": len(self._store),
            "ttl_seconds": self._ttl,
            "max_size": self._max_size,
        }