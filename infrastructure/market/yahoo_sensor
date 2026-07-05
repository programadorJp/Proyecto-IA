"""infrastructure/market/yahoo_sensor.py — AsyncMarketSensor.

Versión mejorada del MarketSensor async: misma fuente de datos (Yahoo
Finance + respaldo fijo), pero con arquitectura en capas:

    _fetch_ticker_sync()      → llamada bloqueante a yfinance (va a threadpool)
    _fetch_one()               → una fila tipada (ActivoData), con semáforo
    percibir_mercado_async()  → orquesta todos los tickers en paralelo

Novedades sobre la versión anterior:
- Config centralizada (MarketConfig) en vez de constantes sueltas.
- ActivoData: dataclass tipado en vez de dict suelto, con .to_dict() para
  seguir alimentando el DataFrame que ya consumen tus agentes.
- Cache TTL: si el dashboard pide los mismos tickers dos veces en 30s,
  no vuelve a golpear Yahoo Finance.
- Circuit breaker: si Yahoo empieza a fallar seguido, usa directamente el
  respaldo en vez de esperar 8s de timeout por cada ticker.
- Métricas básicas vía `stats()`.
"""
from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import asdict, dataclass
from functools import partial
from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf

from infrastructure.common.cache import TTLCache
from infrastructure.common.circuit_breaker import CircuitBreaker
from infrastructure.market.config import MarketConfig

logger = logging.getLogger(__name__)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

# Mismos datos que la versión original — no cambia la lógica de negocio
_ACTIVOS: dict[str, str] = {
    "ALICORC1.LM": "Alicorp",
    "BBVAC1.LM": "BBVA Perú",
    "CPACASC1.LM": "Cementos Pacasmayo",
    "FERREYC1.LM": "Ferreycorp",
    "VOLCABC1.LM": "Volcan Minera",
    "BAP": "Credicorp (BCP)",
    "SCCO": "Southern Copper",
}

_RESPALDO: dict[str, tuple[float, float]] = {
    "ALICORC1.LM": (8.45, 1.20),
    "BBVAC1.LM": (5.30, -0.75),
    "CPACASC1.LM": (4.80, 0.42),
    "FERREYC1.LM": (2.95, 2.10),
    "VOLCABC1.LM": (0.48, -1.50),
    "BAP": (185.20, 0.85),
    "SCCO": (98.60, 1.35),
}


@dataclass(slots=True)
class ActivoData:
    """Fila tipada de mercado — reemplaza el dict suelto de la versión anterior."""

    empresa: str
    ticker: str
    precio: float
    crecimiento_pct: float
    sector: str  # "BVL Real-Time" o "Demo" (fuente del dato)

    def to_dict(self) -> dict:
        """Claves en el formato que ya esperan agents/ y los routers."""
        return {
            "Empresa": self.empresa,
            "Ticker": self.ticker,
            "Precio": self.precio,
            "Crecimiento_%": self.crecimiento_pct,
            "Sector": self.sector,
        }


def _fetch_ticker_sync(ticker: str, timeout: float) -> tuple[float, float, str]:
    """Síncrono — se ejecuta en threadpool. Misma lógica que la versión original."""
    try:
        df = yf.download(
            ticker, period="5d", interval="1d",
            progress=False, auto_adjust=True, timeout=timeout,
        )
        if df is None or df.empty:
            raise ValueError("Empty response")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        col = next((c for c in df.columns if "close" in str(c).lower()), None)
        if col is None:
            raise ValueError("No close column")

        serie = df[col].dropna()
        if len(serie) < 1:
            raise ValueError("Empty series")

        actual = float(serie.iloc[-1])
        cambio = 0.0
        if len(serie) >= 2:
            anterior = float(serie.iloc[-2])
            if anterior > 0:
                cambio = round(((actual - anterior) / anterior) * 100, 2)

        return round(actual, 2), cambio, "BVL Real-Time"

    except Exception as exc:
        logger.debug("yfinance falló para %s: %s — usando respaldo", ticker, exc)
        precio, cambio = _RESPALDO.get(ticker, (10.0, 0.0))
        return precio, cambio, "Demo"


class AsyncMarketSensor:
    """Sensor de mercado async, listo para usarse desde FastAPI."""

    def __init__(self, config: Optional[MarketConfig] = None) -> None:
        self._config = config or MarketConfig.from_env()
        self.activos = _ACTIVOS
        self._semaphore = asyncio.Semaphore(self._config.concurrencia_maxima)
        self._cache: TTLCache[pd.DataFrame] = TTLCache(
            ttl_seconds=self._config.cache_ttl_segundos,
            max_size=self._config.cache_max_size,
        )
        self._circuit = CircuitBreaker(
            umbral_fallos=self._config.circuito_umbral_fallos,
            tiempo_reset=self._config.circuito_tiempo_reset,
        )
        self._stats = {"requests": 0, "fallos": 0, "cache_hits": 0}

    # ── Observabilidad ──

    def stats(self) -> dict:
        return {
            **self._stats,
            "cache": self._cache.stats(),
            "circuito": self._circuit.stats(),
        }

    # ── Una fila ──

    async def _fetch_one(self, ticker: str) -> ActivoData:
        empresa = self.activos.get(ticker, ticker)

        if not self._circuit.permite_llamada():
            # Circuito abierto: no perder tiempo intentando, usa el respaldo directo
            precio, cambio = _RESPALDO.get(ticker, (10.0, 0.0))
            return ActivoData(empresa, ticker, precio, cambio, "Demo (circuito abierto)")

        async with self._semaphore:
            loop = asyncio.get_running_loop()
            try:
                precio, cambio, sector = await loop.run_in_executor(
                    None, partial(_fetch_ticker_sync, ticker, self._config.timeout_segundos)
                )
                if sector == "BVL Real-Time":
                    self._circuit.registrar_exito()
                else:
                    # _fetch_ticker_sync ya cayó a respaldo internamente
                    self._circuit.registrar_fallo()
                return ActivoData(empresa, ticker, precio, cambio, sector)
            except Exception as exc:
                logger.error("Error inesperado para %s: %s", ticker, exc)
                self._circuit.registrar_fallo()
                precio, cambio = _RESPALDO.get(ticker, (10.0, 0.0))
                return ActivoData(empresa, ticker, precio, cambio, "Demo")

    # ── Todos los tickers ──

    async def percibir_mercado_async(
        self, lista_tickers: Optional[list[str]] = None
    ) -> pd.DataFrame:
        tickers = lista_tickers or list(self.activos.keys())
        self._stats["requests"] += 1

        cache_key = ",".join(sorted(tickers))
        if (cacheado := await self._cache.get(cache_key)) is not None:
            self._stats["cache_hits"] += 1
            return cacheado.copy()

        resultados = await asyncio.gather(*(self._fetch_one(t) for t in tickers))
        df = pd.DataFrame([r.to_dict() for r in resultados]) if resultados else pd.DataFrame()

        await self._cache.set(cache_key, df)
        return df

    async def invalidar_cache(self) -> None:
        """Fuerza a que el próximo request vuelva a consultar Yahoo Finance."""
        await self._cache.clear()

    # ── Exportar hechos para el motor CLIPS ──

    async def exportar_hechos_lisp_async(self, df: pd.DataFrame) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(self._escribir_lisp, df))

    @staticmethod
    def _escribir_lisp(df: pd.DataFrame) -> str:
        base = Path(__file__).resolve().parent.parent.parent / "data"
        base.mkdir(exist_ok=True)
        ruta = base / "hechos_mercado.lisp"

        with ruta.open("w", encoding="utf-8") as f:
            f.write("; hechos_mercado.lisp — generado automáticamente\n")
            f.write("(setq hechos-mercado '(\n")
            for _, fila in df.iterrows():
                f.write(
                    f'  ("{fila["Empresa"]}" {fila["Precio"]} '
                    f'{fila["Crecimiento_%"]} "{fila["Sector"]}")\n'
                )
            f.write("))\n")
        return str(ruta)