"""advanced_intelligent_agent.py — Agente Inteligente Mejorado
Análisis completo y respuestas conversacionales."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.intelligent_agent import IntelligentAgent
from agents.news_analyzer import NewsAnalyzer
from agents.prediction_engine import PredictionEngine
from agents.conversational_response import ConversationalResponseGenerator
from agents.market_sensor import MarketSensor


class AdvancedIntelligentAgent:
    """Agente mejorado con análisis completo y respuestas humanas."""
    
    def __init__(self):
        self.base_agent = IntelligentAgent()
        self.news_analyzer = NewsAnalyzer()
        self.prediction_engine = PredictionEngine()
        self.response_generator = ConversationalResponseGenerator()
        self.sensor = MarketSensor()
    
    def analizar_empresa_conversacional(self, ticker):
        """
        Análisis completo conversacional de una empresa.
        Responde como un analista humano experimentado.
        """
        
        # 1. Validar ticker
        if ticker not in self.sensor.activos:
            return f"Error: Ticker {ticker} no encontrado en BVL."
        
        empresa = self.sensor.activos[ticker]
        
        # 2. Obtener datos de mercado
        df = self.sensor.percibir_mercado([ticker])
        precio_actual = df.iloc[0]['Precio'] if len(df) > 0 else 0
        
        # 3. Obtener recomendación técnica/fundamental/sentimiento
        recomendacion_base = self.base_agent.recommendations.evaluar_activo(ticker, precio_actual)
        
        # 4. Obtener análisis de noticias
        tendencia_noticias = self.news_analyzer.analizar_tendencia(ticker)
        resumen_noticias = self.news_analyzer.generar_resumen_noticias(ticker)
        catalistas = self.news_analyzer.detectar_catalistas(ticker)
        
        # 5. Generar predicciones
        pred_corto = self.prediction_engine.predecir_corto_plazo(
            ticker, 
            recomendacion_base['score_final'],
            catalistas
        )
        
        pred_mediano = self.prediction_engine.predecir_mediano_plazo(
            ticker,
            recomendacion_base['score_fundamental'],
            tendencia_noticias['score'] * 100
        )
        
        pred_largo = self.prediction_engine.predecir_largo_plazo(
            ticker,
            recomendacion_base['score_fundamental'],
            70  # sector outlook default
        )
        
        escenarios = self.prediction_engine.generar_escenarios(
            ticker,
            precio_actual,
            recomendacion_base['score_fundamental']
        )
        
        # 6. Compilar datos para respuesta conversacional
        datos_completos = {
            'recomendacion': recomendacion_base,
            'noticias': {
                'resumen': resumen_noticias,
                'tendencia': tendencia_noticias['tendencia']
            },
            'predicciones': {
                'corto_plazo': pred_corto,
                'mediano_plazo': pred_mediano,
                'largo_plazo': pred_largo,
                'escenarios': escenarios
            },
            'catalistas': catalistas
        }
        
        # 7. Generar respuesta conversacional
        respuesta = self.response_generator.generar_analisis_conversacional(
            ticker, empresa, datos_completos
        )
        
        return respuesta
    
    def comparar_empresas_conversacional(self, tickers):
        """Compara empresas de forma conversacional."""
        
        print(f"\nAnalizando {len(tickers)} empresas...\n")
        
        analisis = []
        for ticker in tickers:
            if ticker not in self.sensor.activos:
                continue
            
            empresa = self.sensor.activos[ticker]
            df = self.sensor.percibir_mercado([ticker])
            precio = df.iloc[0]['Precio'] if len(df) > 0 else 0
            
            recomendacion = self.base_agent.recommendations.evaluar_activo(ticker, precio)
            
            analisis.append({
                'ticker': ticker,
                'empresa': empresa,
                'score': recomendacion['score_final'],
                'recomendacion': recomendacion['recomendacion'],
                'tecnico': recomendacion['score_tecnico'],
                'fundamental': recomendacion['score_fundamental']
            })
        
        # Ordenar por score
        analisis.sort(key=lambda x: x['score'], reverse=True)
        
        # Generar respuesta comparativa
        respuesta = f"""COMPARACION DE EMPRESAS:

Analicé {len(analisis)} empresas para ti. Aquí está el ranking:
\n"""
        
        for i, a in enumerate(analisis, 1):
            respuesta += f"""{i}. {a['empresa'].upper()} ({a['ticker']})
   Score: {a['score']}/100 
   Recomendacion: {a['recomendacion']}
   (Tecnico: {a['tecnico']}, Fundamental: {a['fundamental']})

"""
        
        respuesta += f"""\nLA MEJOR OPCION: {analisis[0]['empresa']}
   Por qué: Tiene el score más alto ({analisis[0]['score']}/100) 
   y mejores perspectivas a corto y mediano plazo.

EVITA POR AHORA: {analisis[-1]['empresa']}
   Por qué: Score bajo ({analisis[-1]['score']}/100) con señales 
   negativas. Hay mejores opciones en el mercado.
"""
        
        return respuesta
    
    def obtener_recomendacion_rapida(self, ticker):
        """Obtiene recomendación rápida de una línea."""
        if ticker not in self.sensor.activos:
            return f"Error: Ticker {ticker} no encontrado."
        
        empresa = self.sensor.activos[ticker]
        df = self.sensor.percibir_mercado([ticker])
        precio = df.iloc[0]['Precio'] if len(df) > 0 else 0
        
        recomendacion = self.base_agent.recommendations.evaluar_activo(ticker, precio)
        
        return self.response_generator.generar_respuesta_rapida(
            ticker, empresa, 
            recomendacion['score_final'],
            recomendacion['recomendacion']
        )


if __name__ == "__main__":
    agente = AdvancedIntelligentAgent()
    
    print("\n" + "="*70)
    print("AGENTE INTELIGENTE DE INVERSIONES BVL - CONVERSACIONAL")
    print("="*70)
    
    # Ejemplo: analizar BBVA
    print("\nAnalizando BBVA Peru (BBVAC1.LM)...\n")
    analisis = agente.analizar_empresa_conversacional("BBVAC1.LM")
    print(analisis)
    
    # Comparar empresas
    print("\n\n" + "="*70)
    print("COMPARACION DE EMPRESAS")
    print("="*70)
    comparacion = agente.comparar_empresas_conversacional(
        ["BBVAC1.LM", "ALICORC1.LM", "FERREYC1.LM", "VOLCABC1.LM"]
    )
    print(comparacion)
