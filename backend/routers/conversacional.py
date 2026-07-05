"""backend/routers/conversacional.py — Respuestas en lenguaje natural del
AdvancedIntelligentAgent (análisis detallado, respuesta rápida y comparación).
"""
from fastapi import APIRouter, HTTPException, Depends

from backend.dependencies import get_sensor, get_agente_avanzado
from backend.schemas import AnalisisRequest

router = APIRouter(tags=["Conversacional"])


@router.get("/analisis-conversacional/{ticker}")
def get_analisis_conversacional(
    ticker: str,
    sensor=Depends(get_sensor),
    agente_avanzado=Depends(get_agente_avanzado),
):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    try:
        respuesta = agente_avanzado.analizar_empresa_conversacional(ticker)
        return {
            "ticker":   ticker,
            "empresa":  sensor.activos[ticker],
            "analisis": respuesta,
            "tipo":     "conversacional_detallado",
        }
    except Exception as e:
        raise HTTPException(500, detail=f"Error en análisis: {str(e)}")


@router.get("/respuesta-rapida/{ticker}")
def get_respuesta_rapida(
    ticker: str,
    sensor=Depends(get_sensor),
    agente_avanzado=Depends(get_agente_avanzado),
):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")

    respuesta = agente_avanzado.obtener_recomendacion_rapida(ticker)
    return {"ticker": ticker, "respuesta": respuesta}


@router.post("/comparar-conversacional")
def comparar_conversacional(
    req: AnalisisRequest,
    sensor=Depends(get_sensor),
    agente_avanzado=Depends(get_agente_avanzado),
):
    invalidos = [t for t in req.tickers if t not in sensor.activos]
    if invalidos:
        raise HTTPException(400, detail=f"Tickers inválidos: {invalidos}")

    respuesta = agente_avanzado.comparar_empresas_conversacional(req.tickers)
    return {
        "tickers":     req.tickers,
        "comparacion": respuesta,
        "tipo":        "comparativo_conversacional",
    }