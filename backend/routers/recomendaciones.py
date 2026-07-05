"""backend/routers/recomendaciones.py — Recomendaciones, explicaciones y comparaciones.

Agrupa todo lo que depende del IntelligentAgent y del RecommendationsEngine
para dar una recomendación "directa" sobre un activo o un perfil de inversión.
"""
from fastapi import APIRouter, HTTPException, Depends

from backend.dependencies import get_sensor, get_agente, get_recomendaciones
from backend.schemas import AnalisisRequest

router = APIRouter(tags=["Recomendaciones"])


@router.get("/recomendaciones/{ticker}")
def get_recomendaciones_ticker(
    ticker: str,
    sensor=Depends(get_sensor),
    recomendaciones=Depends(get_recomendaciones),
):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")

    reporte = recomendaciones.evaluar_activo(ticker)
    return {
        "ticker":        ticker,
        "empresa":       sensor.activos[ticker],
        "score_final":   reporte["score_final"],
        "recomendacion": reporte["recomendacion"],
        "confianza":     reporte["confianza"],
        "scores": {
            "tecnico":     reporte["score_tecnico"],
            "fundamental": reporte["score_fundamental"],
            "sentimiento": reporte["score_sentimiento"],
        },
    }


@router.get("/explicacion/{ticker}")
def get_explicacion(
    ticker: str,
    sensor=Depends(get_sensor),
    agente=Depends(get_agente),
):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")

    resultado = agente.obtener_explicacion(ticker)
    return {"ticker": ticker, "explicacion": resultado["explicacion"]}


@router.post("/comparar")
def comparar_activos(
    req: AnalisisRequest,
    sensor=Depends(get_sensor),
    agente=Depends(get_agente),
):
    invalidos = [t for t in req.tickers if t not in sensor.activos]
    if invalidos:
        raise HTTPException(400, detail=f"Tickers inválidos: {invalidos}")

    resultado = agente.comparar_activos(req.tickers)
    return {
        "tickers_comparados": req.tickers,
        "mejor": {
            "ticker":        resultado["mejor"]["ticker"],
            "score":         resultado["mejor"]["score_final"],
            "recomendacion": resultado["mejor"]["recomendacion"],
        },
        "peor": {
            "ticker":        resultado["peor"]["ticker"],
            "score":         resultado["peor"]["score_final"],
            "recomendacion": resultado["peor"]["recomendacion"],
        },
        "comparacion": resultado["comparacion"],
    }


@router.get("/perfil/{perfil}")
def get_recomendaciones_perfil(
    perfil: str = "Moderado",
    agente=Depends(get_agente),
):
    if perfil not in ("Conservador", "Moderado", "Agresivo"):
        raise HTTPException(400, detail="Perfil inválido.")

    resultado = agente.recomendar_para_perfil(perfil)
    return {
        "perfil": perfil,
        "recomendaciones": [
            {
                "ticker":        r["ticker"],
                "score":         r["score_final"],
                "recomendacion": r["recomendacion"],
                "confianza":     r["confianza"],
            }
            for r in resultado["recomendaciones"]
        ],
        "resumen": resultado["resumen"],
    }