# 📈 Pfinance BVL

**Sistema Experto de Asesoría Financiera con IA para la Bolsa de Valores de Lima**

Proyecto académico — UPAO 2026 · Ingeniería de Sistemas e Inteligencia Artificial

---

## 📋 Descripción

Pfinance BVL es un sistema experto que combina un **motor de reglas tipo CLIPS** con un **modelo de lenguaje (Google Gemini)** para generar recomendaciones de inversión personalizadas sobre activos de la Bolsa de Valores de Lima (BVL), según el perfil de riesgo del usuario: **Conservador**, **Moderado** o **Agresivo**.

El sistema analiza precios de mercado en tiempo real, noticias financieras, sentimiento del mercado (clasificado mediante técnicas de *few-shot prompting* y *Chain-of-Thought*) y genera predicciones a corto, mediano y largo plazo, todo presentado a través de un dashboard interactivo y un chat conversacional.

## ✨ Características principales

- **Dashboard de mercado** con precios en tiempo real, gráficas de variación y distribución de portafolio.
- **Motor de reglas CLIPS-style** (90 reglas) que evalúa activos según el perfil de riesgo seleccionado.
- **Chat conversacional** ("Pfinance") que responde preguntas en lenguaje natural sobre empresas, comparaciones y estrategias de inversión.
- **Análisis con IA generativa**: combina precios, noticias y predicciones en un análisis narrativo humanizado.
- **Clasificación de sentimiento** de noticias financieras mediante Transformer (Gemini) con enfoque *few-shot* especializado en el contexto peruano (minería, tipo de cambio, conflictos sociales).
- **Arquitectura asíncrona**: cache TTL y circuit breaker para evitar bloqueos ante fallas o límites de cuota de servicios externos.

## 🏗️ Arquitectura

El proyecto está organizado en capas con responsabilidades claramente separadas:

```
Proyecto-IA/
├── agents/              → Motores de negocio (versión síncrona original)
│   ├── market_sensor.py         → Sensor de precios (Yahoo Finance)
│   ├── expert_brain.py          → Motor de razonamiento con Gemini
│   ├── clips_rules.py           → Motor de reglas CLIPS-style
│   ├── recommendations_engine.py
│   ├── prediction_engine.py
│   ├── news_analyzer.py
│   ├── advanced_intelligent_agent.py
│   └── ...
│
├── backend/              → API REST (FastAPI)
│   ├── main.py                  → Ensamblaje de la app y lifespan
│   ├── dependencies.py          → Singletons inyectados (Depends)
│   ├── config.py                → Variables de entorno
│   ├── schemas.py                → Modelos Pydantic
│   └── routers/
│       ├── info.py               → Estado del sistema (/api, /status)
│       ├── mercado.py            → Precios y tickers
│       ├── analisis.py           → Análisis IA, fichas técnicas, reglas
│       ├── chat.py               → Chat conversacional
│       ├── recomendaciones.py
│       ├── conversacional.py
│       └── pages.py              → Sirve el frontend estático
│
├── infrastructure/        → Capa asíncrona (evita bloquear el event loop)
│   ├── ai/
│   │   └── gemini_brain.py       → AsyncExpertBrain (httpx + cache + circuit breaker)
│   ├── market/
│   │   └── yahoo_sensor/          → AsyncMarketSensor
│   └── common/
│       ├── cache.py               → TTLCache genérico
│       └── circuit_breaker.py     → CircuitBreaker thread-safe
│
├── frontend/
│   ├── index.html                 → Dashboard de análisis de mercado
│   ├── chat.html                  → Chat conversacional
│   └── assets/
│       ├── css/                   → base.css, dashboard.css, chat.css
│       └── js/                    → config.js, dashboard.js, chat.js
│
└── data/
    └── hechos_mercado.lisp        → Hechos exportados para el motor de reglas
```

**Nota de diseño:** los módulos en `agents/` (síncronos) conviven con su contraparte async en `infrastructure/`. Esta última se creó para eliminar bloqueos del event loop de FastAPI durante llamadas de red a Gemini, Yahoo Finance y APIs de noticias — reemplazando `time.sleep()` por `await asyncio.sleep()` en los reintentos, y ejecutando operaciones síncronas costosas en threadpool.

## 🛠️ Tecnologías

| Categoría | Tecnología |
|---|---|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Cliente HTTP async | httpx |
| Datos de mercado | yfinance (Yahoo Finance) |
| IA generativa | Google Gemini API (`gemini-2.5-flash-lite`) |
| Noticias | Alpha Vantage, NewsAPI |
| Motor de reglas | Motor CLIPS-style desarrollado a medida |
| Frontend | HTML, CSS, JavaScript vanilla, Chart.js |
| Validación de datos | Pydantic |

## 🚀 Instalación y ejecución local

### 1. Clonar el repositorio

```bash
git clone https://github.com/programadorJp/Proyecto-IA.git
cd Proyecto-IA
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```dotenv
GEMINI_API_KEY=tu_api_key_de_gemini
ALPHA_VANTAGE_KEY=tu_api_key_de_alpha_vantage
NEWS_API_KEY=tu_api_key_de_newsapi
GEMINI_MODEL=models/gemini-2.5-flash-lite
```

> Obtén tu API key de Gemini gratis en [Google AI Studio](https://aistudio.google.com/).

### 4. Levantar el servidor

```bash
uvicorn backend.main:app --reload --port 8000
```

### 5. Acceder al sistema

| Recurso | URL |
|---|---|
| Dashboard | `http://127.0.0.1:8000/` |
| Chat | `http://127.0.0.1:8000/chat` |
| Documentación interactiva (Swagger) | `http://127.0.0.1:8000/docs` |
| Estado del sistema | `http://127.0.0.1:8000/api` |

## 📡 Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api` | Estado del sistema |
| `GET` | `/activos` | Precios de mercado en tiempo real |
| `GET` | `/tickers` | Lista de tickers disponibles |
| `GET` | `/reglas` | Evaluación del motor CLIPS según perfil |
| `GET` | `/analisis-ia` | Análisis narrativo generado con IA |
| `GET` | `/ficha/{ticker}` | Ficha técnica de una empresa |
| `POST` | `/chat` | Chat conversacional con Pfinance |
| `GET` | `/fundamental/{ticker}` | Salud financiera fundamental |
| `GET` | `/sentimiento/{ticker}` | Sentimiento de noticias (Transformer) |
| `GET` | `/catalistas/{ticker}` | Catalistas positivos/negativos |
| `GET` | `/predicciones/{ticker}` | Predicciones corto/mediano/largo plazo |

## 💹 Activos soportados

| Ticker | Empresa |
|---|---|
| ALICORC1.LM | Alicorp |
| BBVAC1.LM | BBVA Perú |
| CPACASC1.LM | Cementos Pacasmayo |
| FERREYC1.LM | Ferreycorp |
| VOLCABC1.LM | Volcan Minera |
| BAP | Credicorp (BCP) |
| SCCO | Southern Copper |

## ⚠️ Limitaciones conocidas

- El tier gratuito de la API de Gemini limita a 20 requests/día por modelo — para uso intensivo se recomienda habilitar facturación en Google Cloud.
- Los datos de mercado dependen de la disponibilidad de Yahoo Finance; el sistema cuenta con precios de respaldo (modo demo) cuando la fuente en tiempo real no responde.

## 👤 Autor

Desarrollado por **Jota** — estudiante de Ingeniería de Sistemas e Inteligencia Artificial, Universidad Privada Antenor Orrego (UPAO).

## 📄 Licencia

Proyecto académico desarrollado para el curso de Sistemas Expertos — UPAO 2026.