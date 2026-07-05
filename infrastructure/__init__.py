"""infrastructure — adaptadores async a servicios externos.

- common/  → TTLCache y CircuitBreaker, reutilizados por ai/ y market/
- ai/      → AsyncExpertBrain (Gemini)
- market/  → AsyncMarketSensor (Yahoo Finance)

Los módulos originales en agents/ (síncronos) quedan intactos: estas son
versiones async pensadas para usarse detrás de endpoints `async def` en
FastAPI, sin bloquear el event loop.
"""