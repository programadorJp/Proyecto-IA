"""intelligent_agent.py — Agente Inteligente Principal (con esteroides)
Orquesta todos los componentes: sensor, análisis técnico, fundamental, sentimiento y recomendaciones.

Mejora sobre la versión original: los `print()` sueltos (que en un servidor
web ensucian los logs de producción en cada request) se movieron a
`logging`. El comportamiento en modo CLI (__main__) es el mismo.
"""
from __future__ import annotations

import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.market_sensor import MarketSensor
from agents.clips_rules import ClipsRulesEngine
from agents.expert_brain import ExpertBrain
from agents.recommendations_engine import RecommendationsEngine

logger = logging.getLogger(__name__)


class IntelligentAgent:
    """Agente inteligente unificado para análisis de inversiones BVL."""

    def __init__(self):
        self.sensor = MarketSensor()
        self.clips = ClipsRulesEngine()
        self.brain = ExpertBrain()
        self.recommendations = RecommendationsEngine()

    def analizar_mercado(self, tickers: list[str] | None = None, perfil: str = "Moderado") -> dict:
        """
        Análisis completo del mercado:
        1. Percepción de precios (MarketSensor)
        2. Análisis Técnico + Fundamental + Sentimiento
        3. Motor de reglas CLIPS
        4. Recomendaciones inteligentes
        5. Análisis narrativo con Gemini
        """
        lista_tickers = tickers or list(self.sensor.activos.keys())
        df = self.sensor.percibir_mercado(lista_tickers)

        logger.info("Datos obtenidos: %d activos", len(df))

        analisis_detallado = self.recommendations.generar_reporte_completo(
            lista_tickers,
            precios_actual={row['Ticker']: row['Precio'] for _, row in df.iterrows()},
            precios_anterior=None
        )

        logger.info("Top 3 por score: %s", [r['ticker'] for r in analisis_detallado['top_3']])

        reglas = self.clips.evaluar(df, perfil)
        logger.info("Reglas activadas (perfil %s): %d", perfil, len(reglas))

        analisis_ia = self.brain.procesar_estrategia(df)

        return {
            "datos": df,
            "analisis_detallado": analisis_detallado,
            "reglas_clips": reglas,
            "analisis_ia": analisis_ia,
            "perfil": perfil
        }

    def recomendar_para_perfil(self, perfil: str = "Moderado") -> dict:
        """Retorna recomendaciones personalizadas según perfil de riesgo."""
        df = self.sensor.percibir_mercado()

        if perfil == "Conservador":
            filtrados = df[df['Crecimiento_%'].abs() < 2].head(3)
        elif perfil == "Moderado":
            filtrados = df[(df['Crecimiento_%'] >= -2) & (df['Crecimiento_%'] <= 5)].head(3)
        elif perfil == "Agresivo":
            filtrados = df[df['Crecimiento_%'] >= 1].head(3)
        else:
            filtrados = df.head(3)

        tickers = filtrados['Ticker'].tolist()
        reporte = self.recommendations.generar_reporte_completo(tickers)

        return {
            "perfil": perfil,
            "recomendaciones": reporte['reportes'],
            "resumen": f"{len(reporte['reportes'])} activos recomendados para perfil {perfil}"
        }

    def obtener_explicacion(self, ticker: str) -> dict:
        """Retorna explicación detallada de un activo específico."""
        reporte = self.recommendations.evaluar_activo(ticker)
        explicacion = self.recommendations.generar_explicacion(ticker, reporte)
        return {
            "ticker": ticker,
            "reporte": reporte,
            "explicacion": explicacion
        }

    def comparar_activos(self, tickers: list[str]) -> dict:
        """Compara múltiples activos lado a lado."""
        reporte = self.recommendations.generar_reporte_completo(tickers)

        tabla = [
            {
                'Ticker': r['ticker'],
                'Score': r['score_final'],
                'Técnico': r['score_tecnico'],
                'Fund.': r['score_fundamental'],
                'Sent.': r['score_sentimiento'],
                'Rec.': r['recomendacion']
            }
            for r in reporte['reportes']
        ]

        return {
            "comparacion": tabla,
            "mejor": reporte['reportes'][0] if reporte['reportes'] else None,
            "peor": reporte['reportes'][-1] if reporte['reportes'] else None
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agente = IntelligentAgent()

    print("\n[INICIO] AGENTE INTELIGENTE DE INVERSIONES BVL")
    print("=" * 60)
    resultado = agente.analizar_mercado(perfil="Moderado")
    print(resultado["analisis_ia"])

    print("\n✔ Análisis completado.")