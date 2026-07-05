"""infrastructure/ai/config.py — Configuración de AsyncExpertBrain.

Centraliza todo lo que antes eran parámetros sueltos del constructor o
constantes de módulo. Así el brain se configura por variables de entorno
sin tocar código, y es trivial crear una config distinta para tests.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GeminiConfig:
    api_key: str
    modelo: str = "models/gemini-2.5-flash-lite"
    av_key: str = ""
    news_key: str = ""

    timeout_segundos: float = 30.0
    max_reintentos: int = 3

    # Evita regenerar el mismo análisis dos veces en pocos minutos
    cache_ttl_segundos: float = 120.0
    cache_max_size: int = 128

    # Si Gemini falla repetido, deja de insistir por un rato
    circuito_umbral_fallos: int = 5
    circuito_tiempo_reset: float = 30.0

    @classmethod
    def from_env(cls) -> "GeminiConfig":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ ERROR: GEMINI_API_KEY no configurada en .env")

        defaults = cls(api_key=api_key)  # instancia "molde" con los defaults declarados arriba
        return cls(
            api_key=api_key,
            modelo=os.getenv("GEMINI_MODEL", defaults.modelo),
            av_key=os.getenv("ALPHA_VANTAGE_KEY", ""),
            news_key=os.getenv("NEWS_API_KEY", ""),
            timeout_segundos=float(os.getenv("GEMINI_TIMEOUT", defaults.timeout_segundos)),
            max_reintentos=int(os.getenv("GEMINI_MAX_RETRIES", defaults.max_reintentos)),
            cache_ttl_segundos=float(os.getenv("GEMINI_CACHE_TTL", defaults.cache_ttl_segundos)),
        )