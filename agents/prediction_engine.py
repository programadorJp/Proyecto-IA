"""prediction_engine.py — Motor de Predicciones
Predice tendencias futuras basadas en análisis históricos y noticias."""

import random


class PredictionEngine:
    """Motor de predicciones para tendencias de precios."""
    
    def predecir_corto_plazo(self, ticker, score_actual, catalistas):
        """Predice tendencia a corto plazo (1-4 semanas)."""
        # Base: score actual (40% del peso)
        prediccion_base = score_actual
        
        # Catalistas: afectan predicción (60% del peso)
        balance_catalistas = catalistas.get('balance', 0)
        
        # Calcular predicción
        prediccion = (prediccion_base * 0.4) + (balance_catalistas * 10 + 50) * 0.6
        prediccion = max(0, min(100, prediccion))  # Clamp 0-100
        
        # Determinar dirección
        if prediccion >= 65:
            direccion = "ALISTA"
        elif prediccion >= 50:
            direccion = "ESTABLE AL ALZA"
        elif prediccion >= 35:
            direccion = "ESTABLE A LA BAJA"
        else:
            direccion = "BAJISTA"
        
        return {
            "periodo": "4 semanas",
            "prediccion_score": round(prediccion, 1),
            "direccion": direccion,
            "confianza": self._calcular_confianza(score_actual, balance_catalistas)
        }
    
    def predecir_mediano_plazo(self, ticker, score_fundamental, crecimiento_sector):
        """Predice tendencia a mediano plazo (3-6 meses)."""
        # Factor fundamental es más importante a mediano plazo
        prediccion = score_fundamental * 0.7 + (crecimiento_sector + 50) * 0.3
        prediccion = max(0, min(100, prediccion))
        
        if prediccion >= 70:
            direccion = "FUERTE AL ALZA"
        elif prediccion >= 55:
            direccion = "AL ALZA"
        elif prediccion >= 45:
            direccion = "NEUTRAL"
        elif prediccion >= 30:
            direccion = "A LA BAJA"
        else:
            direccion = "FUERTE A LA BAJA"
        
        return {
            "periodo": "3-6 meses",
            "prediccion_score": round(prediccion, 1),
            "direccion": direccion,
            "confianza": "Media a Alta"
        }
    
    def predecir_largo_plazo(self, ticker, score_fundamental, sector_outlook):
        """Predice tendencia a largo plazo (1+ anos)."""
        # A largo plazo, fundamentales son clave
        prediccion = score_fundamental * 0.8 + sector_outlook * 0.2
        prediccion = max(0, min(100, prediccion))
        
        if prediccion >= 75:
            potencial = "MUY ALTO"
            outlook = "Inversión recomendada a largo plazo"
        elif prediccion >= 60:
            potencial = "ALTO"
            outlook = "Buen potencial de crecimiento"
        elif prediccion >= 50:
            potencial = "MODERADO"
            outlook = "Crecimiento en línea con el mercado"
        elif prediccion >= 35:
            potencial = "BAJO"
            outlook = "Crecimiento limitado"
        else:
            potencial = "MUY BAJO"
            outlook = "Presión bajista sostenida"
        
        return {
            "periodo": "1 ano o mas",
            "potencial": potencial,
            "outlook": outlook,
            "prediccion_score": round(prediccion, 1)
        }
    
    def generar_escenarios(self, ticker, precio_actual, score_fundamental, volatilidad=0.1):
        """Genera 3 escenarios: bajista, base, alcista."""
        
        # Escenario bajista (20% probabilidad)
        precio_bajista = precio_actual * (1 - volatilidad * 2)
        cambio_bajista = ((precio_bajista - precio_actual) / precio_actual) * 100
        
        # Escenario base (60% probabilidad)
        precio_base = precio_actual * (1 + (score_fundamental - 50) / 100 * 0.1)
        cambio_base = ((precio_base - precio_actual) / precio_actual) * 100
        
        # Escenario alcista (20% probabilidad)
        precio_alcista = precio_actual * (1 + volatilidad * 2)
        cambio_alcista = ((precio_alcista - precio_actual) / precio_actual) * 100
        
        return {
            "escenario_bajista": {
                "precio_esperado": round(precio_bajista, 2),
                "cambio_porcentaje": round(cambio_bajista, 2),
                "probabilidad": "20%",
                "razon": "Deterioro de fundamentales o noticias negativas inesperadas"
            },
            "escenario_base": {
                "precio_esperado": round(precio_base, 2),
                "cambio_porcentaje": round(cambio_base, 2),
                "probabilidad": "60%",
                "razon": "Ejecución en línea con expectativas"
            },
            "escenario_alcista": {
                "precio_esperado": round(precio_alcista, 2),
                "cambio_porcentaje": round(cambio_alcista, 2),
                "probabilidad": "20%",
                "razon": "Sorpresas positivas o catalizadores inesperados"
            }
        }
    
    def _calcular_confianza(self, score_actual, balance_catalistas):
        """Calcula nivel de confianza en la predicción."""
        # Alta confianza si score es claro y catalistas respaldan
        if (score_actual >= 70 and balance_catalistas > 0) or (score_actual <= 30 and balance_catalistas < 0):
            return "Alta"
        elif 40 <= score_actual <= 60 and abs(balance_catalistas) <= 1:
            return "Baja (zona neutral)"
        else:
            return "Media"
