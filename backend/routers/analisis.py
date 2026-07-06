"""backend/routers/analisis.py — Análisis IA y de mercado por ticker.

Agrupa todo lo que "analiza" un activo desde distintos ángulos:
estrategia con IA, ficha técnica, salud fundamental, sentimiento de
noticias, catalistas y predicciones a distintos plazos.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.concurrency import run_in_threadpool

from backend.dependencies import get_sensor, get_clips, get_brain, get_agente_avanzado
from backend.schemas import AnalisisRequest, AnalisisResponse, ActivoResponse, ReglaResponse
from agents.recommendations_engine import RecommendationsEngine
from agents.news_analyzer import NewsAnalyzer
from agents.prediction_engine import PredictionEngine

router = APIRouter(tags=["Análisis"])


@router.get("/analisis-ia", tags=["IA"])
async def get_analisis_ia(
    tickers: Optional[str] = Query(default=None),
    perfil: str = Query(default="Moderado"),
    sensor=Depends(get_sensor),
    brain=Depends(get_brain),
):
    lista = tickers.split(",") if tickers else list(sensor.activos.keys())[:3]
    df = await run_in_threadpool(sensor.percibir_mercado, lista)
    texto = await brain.procesar_estrategia(df)
    return {"analisis": texto, "perfil": perfil, "activos": lista}


@router.post("/analisis", response_model=AnalisisResponse, tags=["Pipeline completo"])
async def post_analisis(
    req: AnalisisRequest,
    sensor=Depends(get_sensor),
    clips=Depends(get_clips),
    brain=Depends(get_brain),
):
    invalidos = [t for t in req.tickers if t not in sensor.activos]
    if invalidos:
        raise HTTPException(400, detail=f"Tickers inválidos: {invalidos}")

    df = await run_in_threadpool(sensor.percibir_mercado, req.tickers)
    reglas = clips.evaluar(df, req.perfil)
    ia = await brain.procesar_estrategia(df)

    activos = [
        ActivoResponse(
            empresa=row["Empresa"], ticker=row["Ticker"],
            precio=row["Precio"], crecimiento=row["Crecimiento_%"], sector=row["Sector"],
        )
        for _, row in df.iterrows()
    ]
    return AnalisisResponse(
        activos=activos,
        reglas=[ReglaResponse(**r) for r in reglas],
        analisis_ia=ia,
    )

@router.get("/ficha/{ticker}", tags=["IA"])
async def get_ficha(ticker: str, sensor=Depends(get_sensor), brain=Depends(get_brain)):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    nombre = sensor.activos[ticker]
    ficha = await brain.generar_ficha_tecnica(nombre, ticker)
    return {"ticker": ticker, "empresa": nombre, "ficha": ficha}


@router.get("/fundamental/{ticker}")
def get_fundamental(
    ticker: str,
    sensor=Depends(get_sensor),
    recomendaciones: RecommendationsEngine = Depends(_get_recomendaciones := __import__(
        "backend.dependencies", fromlist=["get_recomendaciones"]
    ).get_recomendaciones),
):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    fundamental = recomendaciones.fundamental
    salud = fundamental.analizar_salud_financiera(ticker)
    datos = fundamental.obtener_datos_empresa(ticker)
    return {
        "ticker": ticker,
        "empresa": sensor.activos[ticker],
        "score": salud["score"],
        "salud": salud["salud"],
        "metricas": {
            "p_e": datos.get("p_e"),
            "roe": datos.get("roe"),
            "deuda_capital": datos.get("deuda_capital"),
            "crecimiento_ingresos": datos.get("crecimiento_ingresos"),
            "margen_neto": datos.get("margen_neto"),
        },
    }


@router.get("/sentimiento/{ticker}")
def get_sentimiento(
    ticker: str,
    sensor=Depends(get_sensor),
    recomendaciones: RecommendationsEngine = Depends(_get_recomendaciones),
):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    sentimiento = recomendaciones.sentimiento
    analisis = sentimiento.analizar_sentimiento_detallado(ticker)
    return {
        "ticker": ticker,
        "empresa": sensor.activos[ticker],
        "score": analisis["score"],
        "sentimiento": analisis["sentimiento"],
        "noticias_count": analisis["noticias_count"],
        "positivas": analisis["positivas"],
        "negativas": analisis["negativas"],
        "noticias_top": analisis["noticias_top"],
    }


@router.get("/catalistas/{ticker}")
def get_catalistas(ticker: str, sensor=Depends(get_sensor)):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    news_analyzer = NewsAnalyzer()
    catalistas = news_analyzer.detectar_catalistas(ticker)
    return {
        "ticker": ticker,
        "empresa": sensor.activos[ticker],
        "catalistas_positivos": [
            {"titulo": c.get("titulo"), "impacto": c.get("impacto")}
            for c in catalistas.get("catalistas_positivos", [])
        ],
        "catalistas_negativos": [
            {"titulo": c.get("titulo"), "impacto": c.get("impacto")}
            for c in catalistas.get("catalistas_negativos", [])
        ],
        "balance": catalistas.get("balance", 0),
    }


@router.get("/noticias/{ticker}", tags=["Noticias"])
def get_noticias(ticker: str, sensor=Depends(get_sensor)):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    news_analyzer = NewsAnalyzer()
    noticias = news_analyzer.obtener_noticias_recientes(ticker)
    tendencia = news_analyzer.analizar_tendencia(ticker)
    return {
        "ticker": ticker,
        "empresa": sensor.activos[ticker],
        "tendencia": tendencia,
        "noticias_count": len(noticias),
        "noticias": noticias[:5],
    }


@router.get("/predicciones/{ticker}", tags=["Predicciones"])
def get_predicciones(
    ticker: str,
    sensor=Depends(get_sensor),
    agente_avanzado=Depends(get_agente_avanzado),
):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")

    recomendacion = agente_avanzado.base_agent.recommendations.evaluar_activo(ticker)
    news_analyzer = NewsAnalyzer()
    catalistas = news_analyzer.detectar_catalistas(ticker)
    pred_engine = PredictionEngine()

    pred_corto = pred_engine.predecir_corto_plazo(ticker, recomendacion["score_final"], catalistas)
    pred_mediano = pred_engine.predecir_mediano_plazo(ticker, recomendacion["score_fundamental"], 50)
    pred_largo = pred_engine.predecir_largo_plazo(ticker, recomendacion["score_fundamental"], 70)

    return {
        "ticker": ticker,
        "empresa": sensor.activos[ticker],
        "corto_plazo": pred_corto,
        "mediano_plazo": pred_mediano,
        "largo_plazo": pred_largo,
    }