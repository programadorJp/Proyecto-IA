"""technical_analysis.py — Análisis Técnico (con esteroides)
Calcula indicadores técnicos e identifica patrones.

Mejora sobre la versión original: type hints en los métodos públicos.
"""
from __future__ import annotations

import pandas as pd


class TechnicalAnalysis:
    """Motor de análisis técnico con indicadores estándar."""

    def __init__(self, periodo_short: int = 12, periodo_long: int = 26, periodo_signal: int = 9):
        self.p_short = periodo_short
        self.p_long = periodo_long
        self.p_signal = periodo_signal

    def calcular_sma(self, datos: pd.Series, periodo: int = 20) -> pd.Series:
        """Media Móvil Simple."""
        return datos.rolling(window=periodo).mean()

    def calcular_ema(self, datos: pd.Series, periodo: int = 20) -> pd.Series:
        """Media Móvil Exponencial."""
        return datos.ewm(span=periodo, adjust=False).mean()

    def calcular_rsi(self, datos: pd.Series, periodo: int = 14) -> pd.Series:
        """RSI (Relative Strength Index)."""
        delta = datos.diff()
        ganancia = (delta.where(delta > 0, 0)).rolling(window=periodo).mean()
        perdida = (-delta.where(delta < 0, 0)).rolling(window=periodo).mean()
        rs = ganancia / perdida
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calcular_macd(self, datos: pd.Series):
        """MACD (Moving Average Convergence Divergence)."""
        ema_short = self.calcular_ema(datos, self.p_short)
        ema_long = self.calcular_ema(datos, self.p_long)
        macd = ema_short - ema_long
        signal = macd.ewm(span=self.p_signal, adjust=False).mean()
        histogram = macd - signal
        return macd, signal, histogram

    def calcular_bandas_bollinger(self, datos: pd.Series, periodo: int = 20, desvios: float = 2):
        """Bandas de Bollinger."""
        sma = self.calcular_sma(datos, periodo)
        std = datos.rolling(window=periodo).std()
        banda_sup = sma + (std * desvios)
        banda_inf = sma - (std * desvios)
        return sma, banda_sup, banda_inf

    def generar_score_tecnico(self, precio_actual: float, precio_anterior: float | None = None) -> float:
        """
        Genera score técnico (0-100) basado en el cambio de precio.
        """
        score = 50  # neutral

        if precio_anterior and precio_anterior > 0:
            cambio = ((precio_actual - precio_anterior) / precio_anterior) * 100

            if cambio >= 5:
                score += 30
            elif cambio >= 3:
                score += 20
            elif cambio >= 1:
                score += 10
            elif cambio >= -1:
                score += 5
            elif cambio >= -3:
                score -= 10
            elif cambio >= -5:
                score -= 20
            else:
                score -= 30

        return max(0, min(100, score))

    def evaluar_desde_dataframe(self, df_precios: pd.DataFrame) -> float:
        """
        Evalúa análisis técnico desde un DataFrame con columnas ['Date', 'Close']
        Retorna score técnico promedio.
        """
        if df_precios.empty or len(df_precios) < 2:
            return 50  # neutral

        precios = df_precios['Close'].values
        precio_actual = precios[-1]
        precio_anterior = precios[-2] if len(precios) > 1 else precio_actual

        return self.generar_score_tecnico(precio_actual, precio_anterior)