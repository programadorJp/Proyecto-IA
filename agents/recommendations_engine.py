"""recommendations_engine.py — Motor de Recomendaciones Inteligente (con esteroides)
Combina análisis técnico, fundamental y de sentimiento para generar recomendaciones.

Mejoras sobre la versión original:
- generar_reporte_completo() ahora evalúa los tickers EN PARALELO
  (ThreadPoolExecutor) en vez de uno por uno — con varios tickers el
  ahorro es directamente proporcional a la cantidad.
- Se eliminó una llamada duplicada a generar_score_tecnico() dentro de
  evaluar_activo() (se calculaba el mismo score dos veces).
- Bug corregido: _calcular_confianza() devolvía "Alta " / "Media " / "Baja "
  con un espacio de más al final (quedaba raro en la UI: "Alta  |" con
  doble espacio). Ahora sin trailing space.
- Cache TTL ligero para evaluar_activo() (mismo ticker + mismo precio en
  pocos segundos = mismo resultado, no hace falta recalcular).

La interfaz pública es IDÉNTICA: evaluar_activo(), generar_reporte_completo(),
generar_explicacion().
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from agents._cache import TTLCache
from agents.technical_analysis import TechnicalAnalysis
from agents.fundamental_analysis import FundamentalAnalysis
from agents.sentiment_analysis import SentimentAnalysis


class RecommendationsEngine:
    """Motor de recomendaciones que combina 3 análisis."""

    PESOS = {
        'tecnico': 0.35,
        'fundamental': 0.40,
        'sentimiento': 0.25
    }

    def __init__(self):
        self.tecnico = TechnicalAnalysis()
        self.fundamental = FundamentalAnalysis()
        self.sentimiento = SentimentAnalysis()
        self._cache = TTLCache(ttl_seconds=15.0, max_size=128)

    def evaluar_activo(self, ticker, precio_actual=None, precio_anterior=None):
        """
        Evaluación completa de un activo combinando los 3 análisis.
        Retorna un diccionario con scores y recomendación.
        """
        cache_key = f"{ticker}:{precio_actual}:{precio_anterior}"
        cacheado = self._cache.get(cache_key)
        if cacheado is not None:
            return cacheado

        # Análisis Técnico — se calcula UNA sola vez y se reutiliza abajo
        # (antes se recalculaba de nuevo dentro de 'detalles')
        if precio_actual and precio_anterior:
            score_tecnico = self.tecnico.generar_score_tecnico(precio_actual, precio_anterior)
        else:
            score_tecnico = 50

        score_fundamental = self.fundamental.generar_score_fundamental(ticker)
        score_sentimiento = self.sentimiento.generar_score_sentimiento(ticker)

        score_final = (
            score_tecnico * self.PESOS['tecnico'] +
            score_fundamental * self.PESOS['fundamental'] +
            score_sentimiento * self.PESOS['sentimiento']
        )

        recomendacion = self._generar_recomendacion(score_final)

        resultado = {
            'ticker': ticker,
            'score_tecnico': round(score_tecnico, 1),
            'score_fundamental': round(score_fundamental, 1),
            'score_sentimiento': round(score_sentimiento, 1),
            'score_final': round(score_final, 1),
            'recomendacion': recomendacion,
            'confianza': self._calcular_confianza(score_final),
            'detalles': {
                'tecnico': score_tecnico,  # reutilizado, ya no se recalcula
                'fundamental': self.fundamental.analizar_salud_financiera(ticker),
                'sentimiento': self.sentimiento.analizar_sentimiento_detallado(ticker)
            }
        }

        self._cache.set(cache_key, resultado)
        return resultado

    def _generar_recomendacion(self, score_final):
        """Genera recomendación basada en score (0-100)."""
        if score_final >= 85:
            return "FUERTE COMPRA"
        elif score_final >= 70:
            return "COMPRA"
        elif score_final >= 55:
            return "MANTENER"
        elif score_final >= 40:
            return "VENTA"
        else:
            return "FUERTE VENTA"

    def _calcular_confianza(self, score_final):
        """Calcula nivel de confianza en la recomendación.

        Nota: la versión original devolvía "Baja ", "Alta ", "Media " con un
        espacio de más al final — corregido aquí (.strip()).
        """
        if 40 <= score_final <= 60:
            texto = "Baja"   # zona neutral, menos confianza
        elif score_final < 40 or score_final > 85:
            texto = "Alta"   # extremos, mayor confianza
        else:
            texto = "Media"  # medio, confianza media
        return texto

    def generar_reporte_completo(self, lista_tickers, precios_actual=None, precios_anterior=None):
        """
        Genera reporte completo evaluando múltiples activos EN PARALELO.
        """
        def _evaluar(ticker: str):
            precio_act = precios_actual.get(ticker) if precios_actual else None
            precio_ant = precios_anterior.get(ticker) if precios_anterior else None
            return self.evaluar_activo(ticker, precio_act, precio_ant)

        reportes = []
        with ThreadPoolExecutor(max_workers=min(8, max(len(lista_tickers), 1))) as executor:
            futuros = {executor.submit(_evaluar, t): t for t in lista_tickers}
            for futuro in as_completed(futuros):
                reportes.append(futuro.result())

        # Reordenar según el orden pedido (as_completed no lo garantiza)
        orden = {t: i for i, t in enumerate(lista_tickers)}
        reportes.sort(key=lambda r: orden.get(r["ticker"], 999))
        # Y luego por score final, como en la versión original
        reportes.sort(key=lambda x: x['score_final'], reverse=True)

        return {
            'activos_evaluados': len(reportes),
            'reportes': reportes,
            'top_3': reportes[:3],
            'timestamp': self._get_timestamp()
        }

    def generar_explicacion(self, ticker, reporte):
        """
        Genera una explicación legible del análisis.
        """
        rec = reporte['recomendacion']
        score = reporte['score_final']
        conf = reporte['confianza']

        fund = reporte['detalles']['fundamental']
        sent = reporte['detalles']['sentimiento']

        explicacion = f"""
ANÁLISIS COMPLETO: {ticker}
{'='*50}

RECOMENDACIÓN: {rec}
   Score Final: {score}/100 | Confianza: {conf}

SCORES COMPONENTES:
   • Técnico:      {reporte['score_tecnico']}/100
   • Fundamental:  {reporte['score_fundamental']}/100
   • Sentimiento:  {reporte['score_sentimiento']}/100

ANÁLISIS FUNDAMENTAL:
   Salud: {fund['salud']}
   {fund['detalle']}

ANÁLISIS DE SENTIMIENTO:
   {sent['sentimiento']}
   Noticias positivas: {sent['positivas']}
   Noticias negativas: {sent['negativas']}

CONCLUSIÓN:
   {self._generar_conclusion(score)}
"""
        return explicacion

    def _generar_conclusion(self, score):
        """Genera texto de conclusión basado en el score."""
        if score >= 85:
            return "Excelentes señales de compra. Altamente recomendado para inversión."
        elif score >= 70:
            return "Señales positivas. Buen candidato para inversión."
        elif score >= 55:
            return "Posición neutral. Esperar confirmación o mejor momento."
        elif score >= 40:
            return "Señales negativas. Considerar reducir posición o esperar."
        else:
            return "Señales muy negativas. No recomendado para inversión en este momento."

    @staticmethod
    def _get_timestamp():
        """Retorna timestamp actual."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")