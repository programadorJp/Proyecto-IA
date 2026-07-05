"""backend/routers — paquete con todos los routers de la API.

Cada archivo agrupa endpoints por responsabilidad:
- info.py           → estado general ("/", "/status")
- pages.py          → páginas HTML ("/dashboard", "/chat" GET)
- mercado.py        → datos de mercado y motor CLIPS
- analisis.py       → análisis IA/fundamental/sentimiento/predicciones por ticker
- recomendaciones.py→ recomendaciones, explicación, comparar, perfil
- conversacional.py → respuestas en lenguaje natural
- chat.py           → chat público (POST "/chat")
"""