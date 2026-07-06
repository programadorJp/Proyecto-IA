"""backend/routers/info.py — Endpoints de estado general de la API."""
from fastapi import APIRouter

from backend.config import GEMINI_API_KEY

router = APIRouter(tags=["Info"])


# Cambiamos la ruta de "/" a "/api"
@router.get("/api")   # ← esta es la línea clave
def root():
    return {
        "status":    "ok",
        "proyecto":  "Sistema Experto BVL — UPAO 2026",
        "dashboard": "http://127.0.0.1:8000/dashboard",
        "docs":      "http://127.0.0.1:8000/docs",
        "modo":      "API Key centralizada (dueño del sistema)"
    }


@router.get("/status")
def get_status():
    """Verifica el estado del sistema y la API key."""
    return {
        "status":               "online",
        "api_key_configured":   bool(GEMINI_API_KEY),
        "api_key_preview":      GEMINI_API_KEY[:10] + "..." if GEMINI_API_KEY else None,
        "modo":                 "Todos los usuarios usan la API key del sistema",
        "endpoints_disponibles": [
            "/api", "/dashboard", "/chat", "/activos", "/reglas", "/analisis-ia", "/status"
        ]
    }