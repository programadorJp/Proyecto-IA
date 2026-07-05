"""backend/routers/pages.py — Páginas HTML servidas directamente desde frontend/."""
import os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from backend.config import FRONTEND_DIR

router = APIRouter(tags=["Páginas"])


def _servir_html(nombre_archivo: str, fallback_html: str) -> HTMLResponse:
    ruta = os.path.join(FRONTEND_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return HTMLResponse(fallback_html, status_code=404)
    with open(ruta, encoding="utf-8") as f:
        return HTMLResponse(f.read())


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return _servir_html(
        "index.html",
        "<h1>Dashboard no encontrado. Verifica la carpeta frontend/</h1>"
    )


@router.get("/chat", response_class=HTMLResponse)
def chat_page():
    return _servir_html(
        "chat.html",
        "<h1>💬 Chat Interactivo</h1>"
        "<p>Crea un archivo chat.html en la carpeta frontend/, "
        "o usa el endpoint POST /chat para enviar mensajes.</p>"
    )