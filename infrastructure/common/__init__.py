"""infrastructure/common — utilidades compartidas entre ai/ y market/.

- cache.py            → TTLCache, para no repetir llamadas externas costosas
- circuit_breaker.py  → CircuitBreaker, para no insistir en un servicio caído
"""
from .cache import TTLCache
from .circuit_breaker import CircuitBreaker, EstadoCircuito

__all__ = ["TTLCache", "CircuitBreaker", "EstadoCircuito"]