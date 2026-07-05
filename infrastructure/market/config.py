"""infrastructure/market/config.py — Configuración de AsyncMarketSensor."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MarketConfig:
    concurrencia_maxima: int = 5
    timeout_segundos: float = 8.0

    # Evita golpear Yahoo Finance en cada request del dashboard
    cache_ttl_segundos: float = 30.0
    cache_max_size: int = 64

    # Si Yahoo empieza a fallar seguido, usa el respaldo sin insistir
    circuito_umbral_fallos: int = 5
    circuito_tiempo_reset: float = 60.0

    @classmethod
    def from_env(cls) -> "MarketConfig":
        defaults = cls()  # instancia "molde" con los defaults declarados arriba
        return cls(
            concurrencia_maxima=int(os.getenv("MARKET_MAX_CONCURRENCY", defaults.concurrencia_maxima)),
            timeout_segundos=float(os.getenv("MARKET_TIMEOUT", defaults.timeout_segundos)),
            cache_ttl_segundos=float(os.getenv("MARKET_CACHE_TTL", defaults.cache_ttl_segundos)),
        )