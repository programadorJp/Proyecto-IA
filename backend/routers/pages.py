"""backend/routers/pages.py — Páginas HTML servidas directamente desde frontend/."""
import os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from backend.config import FRONTEND_DIR

router = APIRouter(tags=["Páginas"])


def _servir_html(nombre_archivo: str, fallback_html: str) -> HTMLResponse:
    ruta = os.path.join(FRONTEND_DIR, nombre_archivo)
    if not os.path.exists(ruta):
        return HTMLResponse(fallback_html, status_code=404)
    with open(ruta, encoding="utf-8") as f:
        return HTMLResponse(f.read())


# Ruta raíz: sirve el dashboard (index.html)
@router.get("/", response_class=HTMLResponse)
def raiz():
    return _servir_html(
        "index.html",
        "<h1>Página principal no encontrada. Verifica la carpeta frontend/</h1>"
    )


# Redirigimos /dashboard a / para no duplicar el código ni el archivo
@router.get("/dashboard")
def dashboard_redirect():
    return RedirectResponse(url="/")


# Ruta del chat
@router.get("/chat", response_class=HTMLResponse)
def chat_page():
    return _servir_html(
        "chat.html",
        "<h1>Chat Interactivo</h1>"
        "<p>Crea un archivo chat.html en la carpeta frontend/, "
        "o usa el endpoint POST /chat para enviar mensajes.</p>"
    )