"""agents/_cache.py — Cache TTL simple, síncrona y thread-safe.

Los agentes en agents/ son síncronos (los usa el resto del proyecto vía
requests bloqueantes). Esta es la contraparte de infrastructure/common/cache.py
pero sin asyncio — usa threading.Lock en vez de asyncio.Lock.

Sirve para no repetir llamadas costosas (Gemini, Yahoo Finance) cuando el
mismo dato se pide varias veces seguidas — típico en un dashboard que
refresca cada pocos segundos.
"""
from __future__ import annotations

import time
from threading import Lock
from typing import Any, Optional


class TTLCache:
    def __init__(self, ttl_seconds: float = 60.0, max_size: int = 128) -> None:
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            expires_at, value = item
            if expires_at < time.monotonic():
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if len(self._store) >= self._max_size and key not in self._store:
                oldest_key = next(iter(self._store))
                del self._store[oldest_key]
            self._store[key] = (time.monotonic() + self._ttl, value)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def stats(self) -> dict:
        with self._lock:
            return {"size": len(self._store), "ttl_seconds": self._ttl, "max_size": self._max_size}