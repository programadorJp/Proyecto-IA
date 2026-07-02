"""backend/main.py — API REST con FastAPI
Expone los agentes del proyecto como endpoints HTTP
y sirve el dashboard HTML/CSS/JS desde /frontend"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import sys, os, requests
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.market_sensor              import MarketSensor
from agents.clips_rules                import ClipsRulesEngine
from agents.expert_brain               import ExpertBrain
from agents.intelligent_agent          import IntelligentAgent
from agents.technical_analysis         import TechnicalAnalysis
from agents.fundamental_analysis       import FundamentalAnalysis
from agents.sentiment_analysis         import SentimentAnalysis
from agents.recommendations_engine     import RecommendationsEngine
from agents.advanced_intelligent_agent import AdvancedIntelligentAgent
from agents.news_analyzer              import NewsAnalyzer
from agents.prediction_engine          import PredictionEngine

# ── App ──
app = FastAPI(
    title="Agente BVL — API",
    description="Sistema Experto de Inversiones · UPAO 2026",
    version="1.0.0"
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Ruta a la carpeta frontend ──
FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'frontend')
)

# ── Montar carpeta frontend ──
app.mount(
    "/frontend",
    StaticFiles(directory=FRONTEND_DIR),
    name="frontend"
)

# ── Agentes ──
sensor          = MarketSensor()
clips           = ClipsRulesEngine()
agente          = IntelligentAgent()
recomendaciones = RecommendationsEngine()
agente_avanzado = AdvancedIntelligentAgent()

# ── Brain lazy — se instancia en el primer uso, cuando .env ya está cargado ──
_brain = None

def get_brain() -> ExpertBrain:
    global _brain
    if _brain is None:
        _brain = ExpertBrain()
    return _brain


# ── MODELOS ──

class ActivoResponse(BaseModel):
    empresa:     str
    ticker:      str
    precio:      float
    crecimiento: float
    sector:      str

class ReglaResponse(BaseModel):
    empresa: str
    ticker:  str
    regla:   str
    accion:  str
    icono:   str
    color:   str

class AnalisisRequest(BaseModel):
    tickers: List[str]
    perfil:  str = "Moderado"

class AnalisisResponse(BaseModel):
    activos:     List[ActivoResponse]
    reglas:      List[ReglaResponse]
    analisis_ia: Optional[str] = None

class ChatMessage(BaseModel):
    role: str        # "user" o "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    perfil: str = "Moderado"

@app.post("/chat", tags=["Chat"])
def chat(req: ChatRequest):
    brain = get_brain()
    
    # Construir historial para el prompt
    historial_texto = ""
    for msg in req.history[-6:]:  # últimos 6 mensajes para no exceder tokens
        rol = "Usuario" if msg.role == "user" else "Pfinance"
        historial_texto += f"{rol}: {msg.content}\n"
    
    # Obtener contexto de mercado actual
    df = sensor.percibir_mercado()
    resumen_mercado = "\n".join([
        f"• {row['Empresa']} ({row['Ticker']}): S/. {row['Precio']} "
        f"({'▲' if row['Crecimiento_%'] >= 0 else '▼'} {abs(row['Crecimiento_%'])}%)"
        for _, row in df.iterrows()
    ])
    
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

    respuesta = brain._generar(prompt)
    return {"response": respuesta, "perfil": req.perfil}


# ── ENDPOINTS ──

@app.get("/", tags=["Info"])
def root():
    return {
        "status": "ok",
        "proyecto": "Sistema Experto BVL — UPAO 2026",
        "dashboard": "http://127.0.0.1:8000/dashboard",
        "docs":      "http://127.0.0.1:8000/docs",
        "endpoints": ["/activos", "/reglas", "/analisis", "/analisis-ia", "/tickers", "/ficha/{ticker}"]
    }

@app.get("/dashboard", response_class=HTMLResponse, tags=["Info"])
def dashboard():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse(
            "<h1>Dashboard no encontrado. Verifica la carpeta frontend/</h1>",
            status_code=404
        )
    with open(index_path, encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/tickers", tags=["Mercado"])
def get_tickers():
    return {"tickers": sensor.activos}

@app.get("/activos", response_model=List[ActivoResponse], tags=["Mercado"])
def get_activos(tickers: Optional[str] = Query(default=None)):
    lista = tickers.split(",") if tickers else list(sensor.activos.keys())
    invalidos = [t for t in lista if t not in sensor.activos]
    if invalidos:
        raise HTTPException(400, detail=f"Tickers no reconocidos: {invalidos}")
    df = sensor.percibir_mercado(lista)
    sensor.exportar_hechos_lisp(df)
    return [
        ActivoResponse(
            empresa     = row["Empresa"],
            ticker      = row["Ticker"],
            precio      = row["Precio"],
            crecimiento = row["Crecimiento_%"],
            sector      = row["Sector"]
        ) for _, row in df.iterrows()
    ]

@app.get("/reglas", response_model=List[ReglaResponse], tags=["Motor CLIPS"])
def get_reglas(
    tickers: Optional[str] = Query(default=None),
    perfil:  str = Query(default="Moderado")
):
    if perfil not in ("Conservador", "Moderado", "Agresivo"):
        raise HTTPException(400, detail="Perfil inválido.")
    lista  = tickers.split(",") if tickers else list(sensor.activos.keys())
    df     = sensor.percibir_mercado(lista)
    reglas = clips.evaluar(df, perfil)
    return [ReglaResponse(**r) for r in reglas]

@app.get("/analisis-ia", tags=["IA"])
def get_analisis_ia(
    tickers: Optional[str] = Query(default=None),
    perfil:  str = Query(default="Moderado")
):
    lista = tickers.split(",") if tickers else list(sensor.activos.keys())[:3]
    df    = sensor.percibir_mercado(lista)
    texto = get_brain().procesar_estrategia(df)
    return {"analisis": texto, "perfil": perfil, "activos": lista}

@app.post("/analisis", response_model=AnalisisResponse, tags=["Pipeline completo"])
def post_analisis(req: AnalisisRequest):
    invalidos = [t for t in req.tickers if t not in sensor.activos]
    if invalidos:
        raise HTTPException(400, detail=f"Tickers inválidos: {invalidos}")
    df     = sensor.percibir_mercado(req.tickers)
    reglas = clips.evaluar(df, req.perfil)
    ia     = get_brain().procesar_estrategia(df)
    activos = [
        ActivoResponse(
            empresa     = row["Empresa"],
            ticker      = row["Ticker"],
            precio      = row["Precio"],
            crecimiento = row["Crecimiento_%"],
            sector      = row["Sector"]
        ) for _, row in df.iterrows()
    ]
    return AnalisisResponse(
        activos     = activos,
        reglas      = [ReglaResponse(**r) for r in reglas],
        analisis_ia = ia
    )

@app.get("/ficha/{ticker}", tags=["IA"])
def get_ficha(ticker: str):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    nombre = sensor.activos[ticker]
    ficha  = get_brain().generar_ficha_tecnica(nombre, ticker)
    return {"ticker": ticker, "empresa": nombre, "ficha": ficha}

@app.get("/recomendaciones/{ticker}", tags=["Recomendaciones"])
def get_recomendaciones(ticker: str):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    reporte = recomendaciones.evaluar_activo(ticker)
    return {
        "ticker":       ticker,
        "empresa":      sensor.activos[ticker],
        "score_final":  reporte['score_final'],
        "recomendacion":reporte['recomendacion'],
        "confianza":    reporte['confianza'],
        "scores": {
            "tecnico":     reporte['score_tecnico'],
            "fundamental": reporte['score_fundamental'],
            "sentimiento": reporte['score_sentimiento']
        }
    }

@app.get("/explicacion/{ticker}", tags=["Recomendaciones"])
def get_explicacion(ticker: str):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    resultado = agente.obtener_explicacion(ticker)
    return {"ticker": ticker, "explicacion": resultado['explicacion']}

@app.get("/fundamental/{ticker}", tags=["Análisis"])
def get_fundamental(ticker: str):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    fundamental = RecommendationsEngine().fundamental
    salud = fundamental.analizar_salud_financiera(ticker)
    datos = fundamental.obtener_datos_empresa(ticker)
    return {
        "ticker":  ticker,
        "empresa": sensor.activos[ticker],
        "score":   salud['score'],
        "salud":   salud['salud'],
        "metricas": {
            "p_e":                  datos.get('p_e'),
            "roe":                  datos.get('roe'),
            "deuda_capital":        datos.get('deuda_capital'),
            "crecimiento_ingresos": datos.get('crecimiento_ingresos'),
            "margen_neto":          datos.get('margen_neto')
        }
    }

@app.get("/sentimiento/{ticker}", tags=["Análisis"])
def get_sentimiento(ticker: str):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    sentimiento = RecommendationsEngine().sentimiento
    analisis = sentimiento.analizar_sentimiento_detallado(ticker)
    return {
        "ticker":         ticker,
        "empresa":        sensor.activos[ticker],
        "score":          analisis['score'],
        "sentimiento":    analisis['sentimiento'],
        "noticias_count": analisis['noticias_count'],
        "positivas":      analisis['positivas'],
        "negativas":      analisis['negativas'],
        "noticias_top":   analisis['noticias_top']
    }

@app.post("/comparar", tags=["Análisis"])
def comparar_activos(req: AnalisisRequest):
    invalidos = [t for t in req.tickers if t not in sensor.activos]
    if invalidos:
        raise HTTPException(400, detail=f"Tickers inválidos: {invalidos}")
    resultado = agente.comparar_activos(req.tickers)
    return {
        "tickers_comparados": req.tickers,
        "mejor": {
            "ticker":        resultado['mejor']['ticker'],
            "score":         resultado['mejor']['score_final'],
            "recomendacion": resultado['mejor']['recomendacion']
        },
        "peor": {
            "ticker":        resultado['peor']['ticker'],
            "score":         resultado['peor']['score_final'],
            "recomendacion": resultado['peor']['recomendacion']
        },
        "comparacion": resultado['comparacion']
    }

@app.get("/perfil/{perfil}", tags=["Recomendaciones"])
def get_recomendaciones_perfil(perfil: str = "Moderado"):
    if perfil not in ("Conservador", "Moderado", "Agresivo"):
        raise HTTPException(400, detail="Perfil inválido.")
    resultado = agente.recomendar_para_perfil(perfil)
    return {
        "perfil": perfil,
        "recomendaciones": [
            {
                "ticker":        r['ticker'],
                "score":         r['score_final'],
                "recomendacion": r['recomendacion'],
                "confianza":     r['confianza']
            } for r in resultado['recomendaciones']
        ],
        "resumen": resultado['resumen']
    }

@app.get("/estado-mercado", tags=["Mercado"])
def get_estado_mercado():
    df = sensor.percibir_mercado()
    promedio = df['Crecimiento_%'].mean()
    return {
        "activos_totales":      len(df),
        "promedio_crecimiento": round(promedio, 2),
        "al_alza":              int(len(df[df['Crecimiento_%'] > 0])),
        "a_la_baja":            int(len(df[df['Crecimiento_%'] < 0])),
        "sentimiento_mercado":  (
            "Alcista 📈" if promedio > 1
            else "Bajista 📉" if promedio < -1
            else "Neutral ➡️"
        ),
        "activos": [
            {
                "empresa":    row['Empresa'],
                "ticker":     row['Ticker'],
                "precio":     row['Precio'],
                "crecimiento":row['Crecimiento_%']
            } for _, row in df.iterrows()
        ]
    }

@app.get("/analisis-conversacional/{ticker}", tags=["Conversacional"])
def get_analisis_conversacional(ticker: str):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    try:
        respuesta = agente_avanzado.analizar_empresa_conversacional(ticker)
        return {
            "ticker":  ticker,
            "empresa": sensor.activos[ticker],
            "analisis":respuesta,
            "tipo":    "conversacional_detallado"
        }
    except Exception as e:
        raise HTTPException(500, detail=f"Error en análisis: {str(e)}")

@app.get("/respuesta-rapida/{ticker}", tags=["Conversacional"])
def get_respuesta_rapida(ticker: str):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    respuesta = agente_avanzado.obtener_recomendacion_rapida(ticker)
    return {"ticker": ticker, "respuesta": respuesta}

@app.post("/comparar-conversacional", tags=["Conversacional"])
def comparar_conversacional(req: AnalisisRequest):
    invalidos = [t for t in req.tickers if t not in sensor.activos]
    if invalidos:
        raise HTTPException(400, detail=f"Tickers inválidos: {invalidos}")
    respuesta = agente_avanzado.comparar_empresas_conversacional(req.tickers)
    return {
        "tickers":    req.tickers,
        "comparacion":respuesta,
        "tipo":       "comparativo_conversacional"
    }

@app.get("/noticias/{ticker}", tags=["Noticias"])
def get_noticias(ticker: str):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    news_analyzer = NewsAnalyzer()
    noticias  = news_analyzer.obtener_noticias_recientes(ticker)
    tendencia = news_analyzer.analizar_tendencia(ticker)
    return {
        "ticker":         ticker,
        "empresa":        sensor.activos[ticker],
        "tendencia":      tendencia,
        "noticias_count": len(noticias),
        "noticias":       noticias[:5]
    }

@app.get("/predicciones/{ticker}", tags=["Predicciones"])
def get_predicciones(ticker: str):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    recomendacion = agente_avanzado.base_agent.recommendations.evaluar_activo(ticker)
    news_analyzer = NewsAnalyzer()
    catalistas    = news_analyzer.detectar_catalistas(ticker)
    pred_engine   = PredictionEngine()
    pred_corto    = pred_engine.predecir_corto_plazo(ticker, recomendacion['score_final'], catalistas)
    pred_mediano  = pred_engine.predecir_mediano_plazo(ticker, recomendacion['score_fundamental'], 50)
    pred_largo    = pred_engine.predecir_largo_plazo(ticker, recomendacion['score_fundamental'], 70)
    return {
        "ticker":        ticker,
        "empresa":       sensor.activos[ticker],
        "corto_plazo":   pred_corto,
        "mediano_plazo": pred_mediano,
        "largo_plazo":   pred_largo
    }

@app.get("/catalistas/{ticker}", tags=["Análisis"])
def get_catalistas(ticker: str):
    if ticker not in sensor.activos:
        raise HTTPException(404, detail=f"Ticker '{ticker}' no encontrado.")
    news_analyzer = NewsAnalyzer()
    catalistas    = news_analyzer.detectar_catalistas(ticker)
    return {
        "ticker":  ticker,
        "empresa": sensor.activos[ticker],
        "catalistas_positivos": [
            {"titulo": c.get('titulo'), "impacto": c.get('impacto')}
            for c in catalistas.get('catalistas_positivos', [])
        ],
        "catalistas_negativos": [
            {"titulo": c.get('titulo'), "impacto": c.get('impacto')}
            for c in catalistas.get('catalistas_negativos', [])
        ],
        "balance": catalistas.get('balance', 0)
    }

@app.get("/chat", response_class=HTMLResponse, tags=["Chat"])
def chat_page():
    chat_path = os.path.join(FRONTEND_DIR, "chat.html")
    with open(chat_path, encoding="utf-8") as f:
        return HTMLResponse(f.read())