"""backend/config.py — Configuración y variables de entorno.

Un solo lugar para leer el .env y validar que todo lo necesario
esté presente antes de arrancar el servidor.
"""
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ ERROR: GEMINI_API_KEY no configurada en .env")

# Carpeta del frontend (sibling de backend/), usada para servir
# index.html, chat.html y los estáticos css/js.
FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)