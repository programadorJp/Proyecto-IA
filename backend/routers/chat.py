"""backend/routers/chat.py — Chat público con Pfinance (usa la API key del dueño)."""
from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool

from backend.dependencies import get_sensor, get_brain
from backend.schemas import ChatRequest

router = APIRouter(tags=["Chat"])


@router.post("/chat")
async def chat(
    req: ChatRequest,
    sensor=Depends(get_sensor),
    brain=Depends(get_brain),
):
    """Chat público - todos los usuarios usan la API key del dueño."""

    historial_texto = ""
    for msg in req.history[-6:]:
        rol = "Usuario" if msg.role == "user" else "Pfinance"
        historial_texto += f"{rol}: {msg.content}\n"

    # sensor.percibir_mercado() es síncrona (bloqueante) — ahora que este
    # endpoint es async def, hay que sacarla del event loop manualmente.
    df = await run_in_threadpool(sensor.percibir_mercado)

    resumen_mercado = "\n".join(
        f"• {row['Empresa']} ({row['Ticker']}): S/. {row['Precio']:.2f} "
        f"({'▲' if row['Crecimiento_%'] >= 0 else '▼'} {abs(row['Crecimiento_%']):.2f}%)"
        for _, row in df.iterrows()
    )

    prompt = f"""
Eres Pfinance, un asesor financiero peruano experto en la BVL con 15 años de experiencia.
Eres cercano, directo y honesto. Respondes como si hablaras con un amigo que quiere invertir.

PRECIOS ACTUALES DEL MERCADO:
{resumen_mercado}

HISTORIAL DE CONVERSACIÓN:
{historial_texto if historial_texto else "Esta es la primera consulta."}

Usuario: {req.message}

Responde como Pfinance de forma natural y conversacional.
- Si preguntan por una empresa específica, analízala con los datos del mercado.
- Si piden comparación, compara directamente.
- Si piden recomendación por perfil ({req.perfil}), adáptate a ese perfil.
- Si preguntan precios, usa los datos actuales de arriba.
- Máximo 300 palabras. Sin tecnicismos innecesarios.
- Recuerda el contexto de la conversación anterior.

Pfinance:"""

    respuesta = await brain.generar_respuesta_libre(prompt)
    return {
        "response": respuesta,
        "perfil":   req.perfil,
        "modo":     "API Key centralizada (dueño del sistema)",
    }