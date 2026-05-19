"""
expert_brain.py — Motor de Razonamiento con Gemini AI
Análisis humanizado + noticias reales + predicciones integradas
"""
import requests
import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class ExpertBrain:

    API_KEY    = "AIzaSyDkhp4lle0HU5JJgsEBHFbdfVJWIt7Ru_M"
    BASE_URL   = "https://generativelanguage.googleapis.com/v1beta"
    TIMEOUT    = 30
    REINTENTOS = 3

    AV_KEY   = "HF7PWLS0DOQ3OPZ0"
    NEWS_KEY = "d3ce4824a9094587b58c5a530ff32cfc"

    # GEMINI

    def _get_modelo(self) -> str:
        try:
            resp = requests.get(
                f"{self.BASE_URL}/models?key={self.API_KEY}", timeout=10
            ).json()
            for m in resp.get("models", []):
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    return m["name"]
        except Exception as e:
            print(f"Error al listar modelos: {e}")
        return ""

    def _generar(self, prompt: str) -> str:
        modelo = self._get_modelo()
        if not modelo:
            return "No se encontró modelo disponible."

        for intento in range(self.REINTENTOS):
            try:
                resp = requests.post(
                    f"{self.BASE_URL}/{modelo}:generateContent?key={self.API_KEY}",
                    json={"contents": [{"parts": [{"text": prompt}]}]},
                    timeout=self.TIMEOUT
                ).json()

                if "candidates" in resp:
                    return resp["candidates"][0]["content"]["parts"][0]["text"]

                if resp.get("error", {}).get("code") == 429:
                    print(f"Cuota excedida, esperando 10s... (intento {intento+1})")
                    time.sleep(10)
                    continue

                return "Respuesta inesperada de Gemini."

            except requests.exceptions.Timeout:
                print(f"Timeout intento {intento+1}/{self.REINTENTOS}")
                if intento < self.REINTENTOS - 1:
                    time.sleep(3)
                    continue
                return "Gemini no respondió a tiempo. Intenta de nuevo."

            except requests.exceptions.ConnectionError:
                return "Sin conexión a internet. Verifica tu red."

            except Exception as e:
                if intento < self.REINTENTOS - 1:
                    time.sleep(2)
                    continue
                return f"Error: {str(e)}"

        return "Sin respuesta tras varios intentos."


    # NOTICIAS EXTERNAS (Alpha Vantage + NewsAPI)

    def _buscar_noticias_externas(self, tickers: list) -> str:
        encontradas = []

        for ticker in tickers[:4]:
            # Plan A: Alpha Vantage
            try:
                r = requests.get(
                    f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT"
                    f"&tickers={ticker}&apikey={self.AV_KEY}&limit=2",
                    timeout=5
                ).json()
                if "feed" in r and r["feed"]:
                    for n in r["feed"][:2]:
                        titulo      = n.get("title", "")
                        sentimiento = n.get("overall_sentiment_label", "Neutral")
                        fecha       = n.get("time_published", "")[:8]
                        if titulo:
                            encontradas.append(
                                f"[{ticker}] {titulo} "
                                f"(Sentimiento: {sentimiento}, Fecha: {fecha})"
                            )
                    continue
            except:
                pass

            # Plan B: NewsAPI
            try:
                r = requests.get(
                    f"https://newsapi.org/v2/everything?q={ticker}"
                    f"&language=es&sortBy=publishedAt&pageSize=2"
                    f"&apiKey={self.NEWS_KEY}",
                    timeout=5
                ).json()
                if "articles" in r and r["articles"]:
                    for art in r["articles"][:2]:
                        titulo = art.get("title", "")
                        fecha  = art.get("publishedAt", "")[:10]
                        if titulo and "[Removed]" not in titulo:
                            encontradas.append(f"[{ticker}] {titulo} (Fecha: {fecha})")
            except:
                pass

        return "\n".join(encontradas) if encontradas else ""


    # NOTICIAS LOCALES (NewsAnalyzer)

    def _noticias_locales(self, tickers: list) -> str:
        try:
            from agents.news_analyzer import NewsAnalyzer
            analyzer = NewsAnalyzer()
            bloques  = []

            for ticker in tickers:
                resumen    = analyzer.generar_resumen_noticias(ticker)
                tendencia  = analyzer.analizar_tendencia(ticker)
                catalistas = analyzer.detectar_catalistas(ticker)

                pos = [c["titulo"] for c in catalistas.get("catalistas_positivos", [])]
                neg = [c["titulo"] for c in catalistas.get("catalistas_negativos", [])]

                bloque = f"[{ticker}] Tendencia: {tendencia['tendencia']}\n{resumen}"
                if pos:
                    bloque += f"  ✅ A favor: {', '.join(pos[:2])}\n"
                if neg:
                    bloque += f"  ⚠️ Riesgo: {', '.join(neg[:2])}\n"

                bloques.append(bloque)

            return "\n".join(bloques)
        except Exception as e:
            print(f"NewsAnalyzer no disponible: {e}")
            return ""


    # PREDICCIONES (PredictionEngine)

    def _obtener_predicciones(self, tickers: list, df) -> str:
        try:
            from agents.prediction_engine import PredictionEngine
            from agents.news_analyzer import NewsAnalyzer

            engine   = PredictionEngine()
            analyzer = NewsAnalyzer()
            bloques  = []

            for _, row in df.iterrows():
                ticker     = row["Ticker"]
                precio     = row["Precio"]
                crecimiento = row["Crecimiento_%"]

                # Score aproximado en base al crecimiento del día
                score      = 50 + min(max(crecimiento * 5, -40), 40)
                catalistas = analyzer.detectar_catalistas(ticker)

                corto      = engine.predecir_corto_plazo(ticker, score, catalistas)
                mediano    = engine.predecir_mediano_plazo(ticker, score, 50)
                largo      = engine.predecir_largo_plazo(ticker, score, 70)
                escenarios = engine.generar_escenarios(ticker, precio, score)

                bloques.append(
                    f"[{ticker}]\n"
                    f"  Corto plazo ({corto['periodo']}): {corto['direccion']} "
                    f"— confianza {corto['confianza']}\n"
                    f"  Mediano plazo ({mediano['periodo']}): {mediano['direccion']}\n"
                    f"  Largo plazo ({largo['periodo']}): {largo['potencial']} — {largo['outlook']}\n"
                    f"  Escenario bajista (20%): S/. {escenarios['escenario_bajista']['precio_esperado']} "
                    f"({escenarios['escenario_bajista']['cambio_porcentaje']}%)\n"
                    f"  Escenario base    (60%): S/. {escenarios['escenario_base']['precio_esperado']} "
                    f"({escenarios['escenario_base']['cambio_porcentaje']}%)\n"
                    f"  Escenario alcista (20%): S/. {escenarios['escenario_alcista']['precio_esperado']} "
                    f"({escenarios['escenario_alcista']['cambio_porcentaje']}%)\n"
                )

            return "\n".join(bloques)
        except Exception as e:
            print(f"PredictionEngine no disponible: {e}")
            return ""


    # ANÁLISIS PRINCIPAL

    def procesar_estrategia(self, datos_mercado) -> str:
        """
        Análisis humanizado con noticias + predicciones integradas.
        """
        filas   = []
        tickers = []
        for _, row in datos_mercado.iterrows():
            tendencia = "subiendo" if row["Crecimiento_%"] >= 0 else "bajando"
            filas.append(
                f"• {row['Empresa']} ({row['Ticker']}): "
                f"S/. {row['Precio']} — {tendencia} {abs(row['Crecimiento_%'])}% hoy"
            )
            tickers.append(row["Ticker"])

        resumen_mercado = "\n".join(filas)

        print("Buscando noticias externas...")
        noticias_ext = self._buscar_noticias_externas(tickers)

        print("Consultando base de noticias local...")
        noticias_loc = self._noticias_locales(tickers)

        noticias = ""
        if noticias_ext:
            noticias += "NOTICIAS EN TIEMPO REAL:\n" + noticias_ext + "\n\n"
        if noticias_loc:
            noticias += "ANÁLISIS DETALLADO:\n" + noticias_loc
        if not noticias:
            noticias = "No se encontraron noticias recientes."

        print("Generando predicciones...")
        predicciones = self._obtener_predicciones(tickers, datos_mercado)
        if not predicciones:
            predicciones = "Predicciones no disponibles."

        prompt = f"""
Eres Pfinance, un asesor financiero peruano con 15 años de experiencia en la BVL.
Eres directo, cercano y honesto. Hablas como si le explicaras las cosas a un amigo 
de confianza que quiere invertir pero no domina las finanzas.
Nunca usas jerga innecesaria. Si algo es incierto, lo dices sin rodeos.

Tienes esta información del portafolio de hoy:

═══ PRECIOS DE HOY ═══
{resumen_mercado}

═══ NOTICIAS RECIENTES ═══
{noticias}

═══ PREDICCIONES ═══
{predicciones}

Escribe el análisis de forma natural y conversacional, siguiendo esta estructura:

1. ¿QUÉ ESTÁ PASANDO HOY?
   Explica en 2-3 párrafos lo que ves. No solo leas los números, 
   conéctalos con el contexto. Si algo te llama la atención, dilo.

2. ¿QUÉ DICEN LAS NOTICIAS?
   Relaciona las noticias con los movimientos de precio de cada empresa.
   ¿Hay algo que explique por qué sube o baja?
   Si las noticias contradicen el precio, menciónalo.

3. ¿QUÉ HARÍAS TÚ?
   Para cada empresa: ¿comprarías, venderías o esperarías? 
   Sé directo y explica el razonamiento en términos simples.

4. ¿QUÉ PODRÍA PASAR?
   Usa los 3 escenarios (bajista, base, alcista) de las predicciones 
   para hablar del futuro de las empresas más interesantes.
   Di qué es probable y qué es solo posible.

5. MI CONSEJO FINAL
   Un párrafo personal y directo: como si alguien te preguntara 
   "oye Pfinance, ¿tú qué harías con este portafolio?"

Reglas importantes:
- Español natural, sin tecnicismos innecesarios.
- Emojis solo donde aporten, no en cada frase.
- Párrafos que fluyan, no listas frías de datos.
- Si hay incertidumbre, dila. No finjas saber lo que no se puede saber.
- Máximo 600 palabras en total.
"""
        return self._generar(prompt)


    # FICHA TÉCNICA

    def generar_ficha_tecnica(self, empresa: str, ticker: str) -> str:
        """Ficha técnica humanizada con noticias reales."""
        noticias_ext = self._buscar_noticias_externas([ticker])
        noticias_loc = self._noticias_locales([ticker])

        noticias = ""
        if noticias_ext:
            noticias += noticias_ext + "\n"
        if noticias_loc:
            noticias += noticias_loc
        if not noticias:
            noticias = "Sin noticias recientes disponibles."

        prompt = f"""
Eres un analista financiero que conoce muy bien el mercado peruano.
Escribe una ficha sobre {empresa} ({ticker}) como si se la explicaras 
a alguien que quiere invertir por primera vez. Tono cercano y directo.

Incluye:
- Qué hace esta empresa y por qué importa en el Perú
- En qué sector opera y cómo le va a ese sector actualmente
- Sus principales competidores o empresas relacionadas
- Qué dicen las noticias recientes: {noticias}
- Si fueras a invertir en ella, ¿qué te daría confianza y qué te preocuparía?

Máximo 200 palabras. Tono humano, no de informe corporativo.
"""
        return self._generar(prompt)