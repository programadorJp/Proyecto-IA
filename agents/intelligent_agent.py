"""intelligent_agent.py — Agente Inteligente Principal
Orquesta todos los componentes: sensor, análisis técnico, fundamental, sentimiento y recomendaciones."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.market_sensor import MarketSensor
from agents.clips_rules import ClipsRulesEngine
from agents.expert_brain import ExpertBrain
from agents.technical_analysis import TechnicalAnalysis
from agents.fundamental_analysis import FundamentalAnalysis
from agents.sentiment_analysis import SentimentAnalysis
from agents.recommendations_engine import RecommendationsEngine


class IntelligentAgent:
    """Agente inteligente unificado para análisis de inversiones BVL."""
    
    def __init__(self):
        self.sensor = MarketSensor()
        self.clips = ClipsRulesEngine()
        self.brain = ExpertBrain()
        self.recommendations = RecommendationsEngine()
    
    def analizar_mercado(self, tickers=None, perfil="Moderado"):
        """
        Análisis completo del mercado:
        1. Percepción de precios (MarketSensor)
        2. Análisis Técnico + Fundamental + Sentimiento
        3. Motor de reglas CLIPS
        4. Recomendaciones inteligentes
        5. Análisis narrativo con Gemini
        """
        # 1. Obtener datos del mercado
        lista_tickers = tickers or list(self.sensor.activos.keys())
        df = self.sensor.percibir_mercado(lista_tickers)
        
        print(f"\n[OK] Datos obtenidos: {len(df)} activos")
        print(df[["Empresa", "Precio", "Crecimiento_%"]].to_string(index=False))
        
        # 2. Análisis combinado (Técnico + Fundamental + Sentimiento)
        print(f"\n[ANALISIS] Ejecutando análisis combinado...")
        analisis_detallado = self.recommendations.generar_reporte_completo(
            lista_tickers,
            precios_actual={row['Ticker']: row['Precio'] for _, row in df.iterrows()},
            precios_anterior=None
        )
        
        # 3. Mostrar top 3 recomendaciones
        print(f"\n[TOP 3] ACTIVOS POR SCORE:")
        for i, reporte in enumerate(analisis_detallado['top_3'], 1):
            print(f"\n   {i}. {reporte['ticker']}")
            print(f"      Score: {reporte['score_final']}/100 | {reporte['recomendacion']}")
            print(f"      Tecnico: {reporte['score_tecnico']} | Fundamental: {reporte['score_fundamental']} | Sentimiento: {reporte['score_sentimiento']}")
        
        # 4. Motor de reglas CLIPS
        print(f"\n[CLIPS] Reglas activadas - Perfil: {perfil}")
        reglas = self.clips.evaluar(df, perfil)
        for r in reglas[:5]:  # mostrar top 5
            print(f"   {r['icono']} {r['empresa']:25s} | {r['accion'][:50]}")
        
        # 5. Análisis IA (Gemini)
        print(f"\n[IA] Análisis de IA (Gemini)...")
        analisis_ia = self.brain.procesar_estrategia(df)
        print(analisis_ia)
        
        return {
            "datos": df,
            "analisis_detallado": analisis_detallado,
            "reglas_clips": reglas,
            "analisis_ia": analisis_ia,
            "perfil": perfil
        }
    
    def recomendar_para_perfil(self, perfil="Moderado"):
        """
        Retorna recomendaciones personalizadas según perfil de riesgo.
        """
        df = self.sensor.percibir_mercado()
        
        # Filtrar según perfil
        if perfil == "Conservador":
            # Buscar activos con baja volatilidad y sector financiero
            filtrados = df[df['Crecimiento_%'].abs() < 2].head(3)
        elif perfil == "Moderado":
            # Balance entre riesgo y retorno
            filtrados = df[(df['Crecimiento_%'] >= -2) & (df['Crecimiento_%'] <= 5)].head(3)
        elif perfil == "Agresivo":
            # Alta volatilidad, potencial de crecimiento
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
    
    def obtener_explicacion(self, ticker):
        """
        Retorna explicación detallada de un activo específico.
        """
        reporte = self.recommendations.evaluar_activo(ticker)
        explicacion = self.recommendations.generar_explicacion(ticker, reporte)
        return {
            "ticker": ticker,
            "reporte": reporte,
            "explicacion": explicacion
        }
    
    def comparar_activos(self, tickers):
        """
        Compara múltiples activos lado a lado.
        """
        reporte = self.recommendations.generar_reporte_completo(tickers)
        
        # Tabla comparativa
        tabla = []
        for r in reporte['reportes']:
            tabla.append({
                'Ticker': r['ticker'],
                'Score': r['score_final'],
                'Técnico': r['score_tecnico'],
                'Fund.': r['score_fundamental'],
                'Sent.': r['score_sentimiento'],
                'Rec.': r['recomendacion']
            })
        
        return {
            "comparacion": tabla,
            "mejor": reporte['reportes'][0] if reporte['reportes'] else None,
            "peor": reporte['reportes'][-1] if reporte['reportes'] else None
        }


if __name__ == "__main__":
    agente = IntelligentAgent()
    
    # Análisis completo
    print("\n[INICIO] AGENTE INTELIGENTE DE INVERSIONES BVL")
    print("=" * 60)
    resultado = agente.analizar_mercado(perfil="Moderado")
    
    print("\n✔ Análisis completado.")
