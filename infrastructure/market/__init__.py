"""infrastructure/market — Integración async con Yahoo Finance.

- config.py       → MarketConfig, leída desde .env
- exceptions.py   → excepciones tipadas
- yahoo_sensor.py → AsyncMarketSensor, con cache TTL y circuit breaker
"""
from .config import MarketConfig
from .exceptions import MarketDataError, TickerDesconocidoError
from .yahoo_sensor import ActivoData, AsyncMarketSensor

__all__ = [
    "AsyncMarketSensor",
    "ActivoData",
    "MarketConfig",
    "MarketDataError",
    "TickerDesconocidoError",
]