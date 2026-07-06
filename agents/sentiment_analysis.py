"""sentiment_analysis.py — Análisis de Sentimiento (con esteroides)
Evalúa sentimiento de noticias y tendencias sociales.

Mejora sobre la versión original: se eliminó `import random` (no se usaba
en ningún lado — dead import) y se agregaron type hints.
"""
from __future__ import annotations


class SentimentAnalysis:
    """Motor de análisis de sentimiento para mercado BVL."""

    NOTICIAS_DB = {
        'ALICORC1.LM': [
            {'titulo': 'Alicorp reporta resultados positivos Q1 2024', 'sentimiento': 0.75, 'fecha': -5},
            {'titulo': 'Expansión de plantas en Perú genera optimismo', 'sentimiento': 0.65, 'fecha': -8},
            {'titulo': 'Competencia del sector presiona márgenes', 'sentimiento': -0.45, 'fecha': -15},
        ],
        'BBVAC1.LM': [
            {'titulo': 'BBVA Perú supera estimaciones de ganancias', 'sentimiento': 0.80, 'fecha': -3},
            {'titulo': 'Tasas de interés favorecen a bancos', 'sentimiento': 0.70, 'fecha': -7},
            {'titulo': 'Regulación bancaria más rigurosa se aproxima', 'sentimiento': -0.30, 'fecha': -12},
        ],
        'CPACASC1.LM': [
            {'titulo': 'Construcción de vivienda se desacelera', 'sentimiento': -0.55, 'fecha': -4},
            {'titulo': 'Nuevos proyectos de infraestructura en Perú', 'sentimiento': 0.60, 'fecha': -10},
            {'titulo': 'Cementos Pacasmayo moderniza capacidades', 'sentimiento': 0.50, 'fecha': -14},
        ],
        'FERREYC1.LM': [
            {'titulo': 'Ferreycorp abre nuevas sucursales', 'sentimiento': 0.70, 'fecha': -2},
            {'titulo': 'Consumo de ferretería en alza durante 2024', 'sentimiento': 0.65, 'fecha': -6},
            {'titulo': 'Competencia de retail online afecta ventas', 'sentimiento': -0.40, 'fecha': -18},
        ],
        'VOLCABC1.LM': [
            {'titulo': 'Precios de cobre al alza mejoran perspectivas', 'sentimiento': 0.85, 'fecha': -2},
            {'titulo': 'Volcan aumenta producción de zinc', 'sentimiento': 0.75, 'fecha': -6},
            {'titulo': 'Regulación ambiental más estricta en minería', 'sentimiento': -0.60, 'fecha': -9},
        ],
        'BAP': [
            {'titulo': 'Credicorp reporta sólido desempeño en 2024', 'sentimiento': 0.80, 'fecha': -1},
            {'titulo': 'Confianza del consumidor favorece operaciones', 'sentimiento': 0.70, 'fecha': -5},
            {'titulo': 'Ciberataques requieren mayor inversión en seguridad', 'sentimiento': -0.25, 'fecha': -16},
        ],
        'SCCO': [
            {'titulo': 'Southern Copper genera máximos históricos de ganancia', 'sentimiento': 0.90, 'fecha': -1},
            {'titulo': 'Demanda global de cobre se fortalece', 'sentimiento': 0.85, 'fecha': -4},
            {'titulo': 'Huelga de empleados afecta producción', 'sentimiento': -0.70, 'fecha': -11},
        ]
    }

    def obtener_noticias_recientes(self, ticker: str, dias: int = 30) -> list[dict]:
        """Obtiene noticias de los últimos N días para un ticker."""
        noticias = self.NOTICIAS_DB.get(ticker, [])
        return [n for n in noticias if abs(n['fecha']) <= dias]

    def generar_score_sentimiento(self, ticker: str, ventana_dias: int = 30) -> float:
        """
        Calcula score de sentimiento (0-100) basado en:
        - Promedio ponderado de sentimientos recientes (más reciente = más peso)
        - Número de noticias positivas vs negativas
        """
        noticias = self.obtener_noticias_recientes(ticker, ventana_dias)

        if not noticias:
            return 50  # neutral si no hay noticias

        sentimientos_ponderados = []
        for noticia in noticias:
            dias_atras = abs(noticia['fecha'])
            peso = 1.0 / (1 + (dias_atras / 5))  # exponential decay
            sentimiento_norm = (noticia['sentimiento'] + 1) / 2 * 100  # escala 0-100
            sentimientos_ponderados.append(sentimiento_norm * peso)

        total_peso = sum(1.0 / (1 + (abs(n['fecha']) / 5)) for n in noticias)
        score_promedio = sum(sentimientos_ponderados) / total_peso if total_peso > 0 else 50

        positivas = sum(1 for n in noticias if n['sentimiento'] > 0)
        ratio = positivas / len(noticias) if noticias else 0.5

        if ratio > 0.7:
            score_promedio = min(100, score_promedio + 10)
        elif ratio < 0.3:
            score_promedio = max(0, score_promedio - 10)

        return max(0, min(100, score_promedio))

    def analizar_sentimiento_detallado(self, ticker: str) -> dict:
        """Análisis detallado de sentimiento con noticias."""
        noticias = self.obtener_noticias_recientes(ticker, 30)
        score = self.generar_score_sentimiento(ticker)

        if score >= 70:
            sentimiento_general = "Muy Positivo 😊"
        elif score >= 55:
            sentimiento_general = "Positivo 📈"
        elif score >= 45:
            sentimiento_general = "Neutral ➡️"
        elif score >= 30:
            sentimiento_general = "Negativo 📉"
        else:
            sentimiento_general = "Muy Negativo 😟"

        resumen_noticias = []
        for noticia in noticias[:3]:
            icono = "✅" if noticia['sentimiento'] > 0 else "❌"
            resumen_noticias.append(f"{icono} {noticia['titulo']}")

        return {
            "score": score,
            "sentimiento": sentimiento_general,
            "noticias_count": len(noticias),
            "noticias_top": resumen_noticias,
            "positivas": sum(1 for n in noticias if n['sentimiento'] > 0),
            "negativas": sum(1 for n in noticias if n['sentimiento'] < 0)
        }