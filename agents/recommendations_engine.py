"""recommendations_engine.py — Motor de Recomendaciones Inteligente
Combina análisis técnico, fundamental y de sentimiento para generar recomendaciones."""

from agents.technical_analysis import TechnicalAnalysis
from agents.fundamental_analysis import FundamentalAnalysis
from agents.sentiment_analysis import SentimentAnalysis


class RecommendationsEngine:
    """Motor de recomendaciones que combina 3 análisis."""
    
    def __init__(self):
        self.tecnico = TechnicalAnalysis()
        self.fundamental = FundamentalAnalysis()
        self.sentimiento = SentimentAnalysis()
    
    # Pesos para combinar análisis (pueden ajustarse)
    PESOS = {
        'tecnico': 0.35,
        'fundamental': 0.40,
        'sentimiento': 0.25
    }
    
    def evaluar_activo(self, ticker, precio_actual=None, precio_anterior=None):
        """
        Evaluación completa de un activo combinando los 3 análisis.
        Retorna un diccionario con scores y recomendación.
        """
        # Análisis Técnico
        if precio_actual and precio_anterior:
            score_tecnico = self.tecnico.generar_score_tecnico(precio_actual, precio_anterior)
        else:
            score_tecnico = 50
        
        # Análisis Fundamental
        score_fundamental = self.fundamental.generar_score_fundamental(ticker)
        
        # Análisis de Sentimiento
        score_sentimiento = self.sentimiento.generar_score_sentimiento(ticker)
        
        # Score final ponderado
        score_final = (
            score_tecnico * self.PESOS['tecnico'] +
            score_fundamental * self.PESOS['fundamental'] +
            score_sentimiento * self.PESOS['sentimiento']
        )
        
        # Generar recomendación basada en score
        recomendacion = self._generar_recomendacion(score_final)
        
        return {
            'ticker': ticker,
            'score_tecnico': round(score_tecnico, 1),
            'score_fundamental': round(score_fundamental, 1),
            'score_sentimiento': round(score_sentimiento, 1),
            'score_final': round(score_final, 1),
            'recomendacion': recomendacion,
            'confianza': self._calcular_confianza(score_final),
            'detalles': {
                'tecnico': self.tecnico.generar_score_tecnico(precio_actual or 0, precio_anterior or 0),
                'fundamental': self.fundamental.analizar_salud_financiera(ticker),
                'sentimiento': self.sentimiento.analizar_sentimiento_detallado(ticker)
            }
        }
    
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
        """Calcula nivel de confianza en la recomendación."""
        if 40 <= score_final <= 60:
            return "Baja "  # zona neutral, menos confianza
        elif score_final < 40 or score_final > 85:
            return "Alta "  # extremos, mayor confianza
        else:
            return "Media "  # medio, confianza media
    
    def generar_reporte_completo(self, lista_tickers, precios_actual=None, precios_anterior=None):
        """
        Genera reporte completo evaluando múltiples activos.
        """
        reportes = []
        
        for ticker in lista_tickers:
            precio_act = precios_actual.get(ticker) if precios_actual else None
            precio_ant = precios_anterior.get(ticker) if precios_anterior else None
            
            reporte = self.evaluar_activo(ticker, precio_act, precio_ant)
            reportes.append(reporte)
        
        # Ordenar por score final (mayor primero)
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
        
        # Detalles
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
