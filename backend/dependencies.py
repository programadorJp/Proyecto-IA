"""backend/dependencies.py — Contenedor de dependencias (singletons)."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.market_sensor import MarketSensor
    from agents.clips_rules import ClipsRulesEngine
    from infrastructure.ai.gemini_brain import AsyncExpertBrain
    from agents.intelligent_agent import IntelligentAgent
    from agents.recommendations_engine import RecommendationsEngine
    from agents.advanced_intelligent_agent import AdvancedIntelligentAgent

_sensor:          "MarketSensor | None"                = None
_clips:           "ClipsRulesEngine | None"             = None
_brain:           "AsyncExpertBrain | None"             = None
_agente:          "IntelligentAgent | None"             = None
_recomendaciones: "RecommendationsEngine | None"        = None
_agente_avanzado: "AdvancedIntelligentAgent | None"     = None


def init_dependencies() -> None:
    """Instancia todos los singletons. Llamar una sola vez al arrancar la app."""
    global _sensor, _clips, _brain, _agente, _recomendaciones, _agente_avanzado

    from agents.market_sensor import MarketSensor
    from agents.clips_rules import ClipsRulesEngine
    from infrastructure.ai.gemini_brain import AsyncExpertBrain
    from agents.intelligent_agent import IntelligentAgent
    from agents.recommendations_engine import RecommendationsEngine
    from agents.advanced_intelligent_agent import AdvancedIntelligentAgent

    _sensor          = MarketSensor()
    _clips           = ClipsRulesEngine()
    _brain           = AsyncExpertBrain()     # usa GEMINI_API_KEY del .env (GeminiConfig.from_env())
    _agente          = IntelligentAgent()
    _recomendaciones = RecommendationsEngine()
    _agente_avanzado = AdvancedIntelligentAgent()


async def cerrar_dependencies() -> None:
    """Cierra recursos async al apagar la app (cliente httpx del brain)."""
    if _brain is not None:
        await _brain.aclose()


def get_sensor() -> "MarketSensor":
    assert _sensor is not None, "Sensor no inicializado. ¿Falta el lifespan en main.py?"
    return _sensor


def get_clips() -> "ClipsRulesEngine":
    assert _clips is not None, "CLIPS no inicializado. ¿Falta el lifespan en main.py?"
    return _clips


def get_brain() -> "AsyncExpertBrain":
    assert _brain is not None, "Brain no inicializado. ¿Falta el lifespan en main.py?"
    return _brain


def get_agente() -> "IntelligentAgent":
    assert _agente is not None, "Agente no inicializado. ¿Falta el lifespan en main.py?"
    return _agente


def get_recomendaciones() -> "RecommendationsEngine":
    assert _recomendaciones is not None, "Recomendaciones no inicializado. ¿Falta el lifespan en main.py?"
    return _recomendaciones


def get_agente_avanzado() -> "AdvancedIntelligentAgent":
    assert _agente_avanzado is not None, "Agente avanzado no inicializado. ¿Falta el lifespan en main.py?"
    return _agente_avanzado