"""infrastructure/ai/exceptions.py — Errores propios de la capa Gemini.

Antes los errores se devolvían como strings ("Error de Gemini: ...",
"Sin conexión a internet."), mezclando el caso de éxito y el de error en
el mismo tipo de retorno. Ahora el transporte HTTP levanta excepciones
tipadas; los métodos públicos (procesar_estrategia, generar_ficha_tecnica)
las atrapan en la frontera y ahí sí devuelven el string amigable para el
usuario final — pero internamente el flujo de errores es explícito.
"""


class GeminiError(Exception):
    """Error base para cualquier falla al hablar con Gemini."""


class GeminiRateLimitError(GeminiError):
    """Gemini respondió 429 o reportó alta demanda."""


class GeminiTimeoutError(GeminiError):
    """Gemini no respondió dentro del timeout configurado."""


class GeminiConnectionError(GeminiError):
    """No hay conexión de red hacia Gemini."""


class CircuitoAbiertoError(GeminiError):
    """El circuit breaker está abierto: se rechaza la llamada sin intentarla."""