"""agents/_circuit_breaker.py — Circuit breaker síncrono, thread-safe.

Evita insistir en llamar a un servicio externo que ya está fallando (Gemini,
Yahoo Finance, APIs de noticias). Tras `umbral_fallos` fallos consecutivos
se ABRE y rechaza intentos de inmediato durante `tiempo_reset` segundos, en
vez de esperar timeouts repetidos en cada request del dashboard.
"""
from __future__ import annotations

import time
from enum import Enum, auto
from threading import Lock


class EstadoCircuito(Enum):
    CERRADO = auto()
    ABIERTO = auto()
    SEMIABIERTO = auto()


class CircuitBreaker:
    def __init__(self, umbral_fallos: int = 5, tiempo_reset: float = 30.0) -> None:
        self._umbral = umbral_fallos
        self._tiempo_reset = tiempo_reset
        self._fallos = 0
        self._estado = EstadoCircuito.CERRADO
        self._abierto_desde: float | None = None
        self._lock = Lock()

    @property
    def estado(self) -> EstadoCircuito:
        with self._lock:
            if self._estado is EstadoCircuito.ABIERTO and self._abierto_desde is not None:
                if time.monotonic() - self._abierto_desde >= self._tiempo_reset:
                    self._estado = EstadoCircuito.SEMIABIERTO
            return self._estado

    def permite_llamada(self) -> bool:
        return self.estado is not EstadoCircuito.ABIERTO

    def registrar_exito(self) -> None:
        with self._lock:
            self._fallos = 0
            self._estado = EstadoCircuito.CERRADO
            self._abierto_desde = None

    def registrar_fallo(self) -> None:
        with self._lock:
            self._fallos += 1
            if self._fallos >= self._umbral:
                self._estado = EstadoCircuito.ABIERTO
                self._abierto_desde = time.monotonic()

    def stats(self) -> dict:
        return {
            "estado": self.estado.name,
            "fallos_consecutivos": self._fallos,
            "umbral_fallos": self._umbral,
            "tiempo_reset_segundos": self._tiempo_reset,
        }