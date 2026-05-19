"""fundamental_analysis.py — Análisis Fundamental
Evalúa métricas financieras fundamentales de empresas BVL."""

import pandas as pd


class FundamentalAnalysis:
    """Motor de análisis fundamental."""
    
    # Datos financieros aproximados de empresas BVL (2024)
    # Formato: {ticker: {metricas}}
    DATOS_EMPRESAS = {
        'ALICORC1.LM': {
            'nombre': 'Alicorp',
            'sector': 'Consumo',
            'p_e': 12.5,
            'roe': 15.2,
            'deuda_capital': 0.45,
            'flujo_caja': 850,  # millones
            'crecimiento_ingresos': 8.5,
            'margen_neto': 5.2,
            'activos': 15000,
            'salud_financiera': 'Buena'
        },
        'BBVAC1.LM': {
            'nombre': 'BBVA Perú',
            'sector': 'Financiero',
            'p_e': 10.8,
            'roe': 18.5,
            'deuda_capital': 0.25,
            'flujo_caja': 2100,
            'crecimiento_ingresos': 6.2,
            'margen_neto': 14.8,
            'activos': 85000,
            'salud_financiera': 'Excelente'
        },
        'CPACASC1.LM': {
            'nombre': 'Cementos Pacasmayo',
            'sector': 'Construcción',
            'p_e': 13.2,
            'roe': 12.5,
            'deuda_capital': 0.55,
            'flujo_caja': 450,
            'crecimiento_ingresos': 4.1,
            'margen_neto': 8.5,
            'activos': 8500,
            'salud_financiera': 'Moderada'
        },
        'FERREYC1.LM': {
            'nombre': 'Ferreycorp',
            'sector': 'Retail',
            'p_e': 14.5,
            'roe': 16.8,
            'deuda_capital': 0.35,
            'flujo_caja': 650,
            'crecimiento_ingresos': 9.5,
            'margen_neto': 7.2,
            'activos': 12000,
            'salud_financiera': 'Buena'
        },
        'VOLCABC1.LM': {
            'nombre': 'Volcan Minera',
            'sector': 'Minería',
            'p_e': 9.8,
            'roe': 22.5,
            'deuda_capital': 0.60,
            'flujo_caja': 1200,
            'crecimiento_ingresos': 11.2,
            'margen_neto': 12.5,
            'activos': 18000,
            'salud_financiera': 'Volatil'
        },
        'BAP': {
            'nombre': 'Credicorp (BCP)',
            'sector': 'Financiero',
            'p_e': 11.2,
            'roe': 19.8,
            'deuda_capital': 0.20,
            'flujo_caja': 3500,
            'crecimiento_ingresos': 7.5,
            'margen_neto': 16.2,
            'activos': 150000,
            'salud_financiera': 'Excelente'
        },
        'SCCO': {
            'nombre': 'Southern Copper',
            'sector': 'Minería',
            'p_e': 8.9,
            'roe': 25.5,
            'deuda_capital': 0.40,
            'flujo_caja': 4200,
            'crecimiento_ingresos': 13.5,
            'margen_neto': 24.5,
            'activos': 45000,
            'salud_financiera': 'Excelente'
        }
    }
    
    def obtener_datos_empresa(self, ticker):
        """Obtiene datos fundamentales de una empresa."""
        return self.DATOS_EMPRESAS.get(ticker, {})
    
    def generar_score_fundamental(self, ticker):
        """
        Calcula score fundamental (0-100) basado en:
        - P/E (lower is better, but not too low)
        - ROE (return on equity)
        - Deuda/Capital (lower is better)
        - Crecimiento de ingresos
        - Margen neto
        """
        datos = self.obtener_datos_empresa(ticker)
        if not datos:
            return 50  # neutral si no hay datos
        
        score = 50
        
        # P/E: rango ideal 10-15
        pe = datos.get('p_e', 12)
        if 10 <= pe <= 15:
            score += 15
        elif 8 <= pe < 10:
            score += 10
        elif 15 < pe <= 18:
            score += 5
        else:
            score -= 5
        
        # ROE: >15% es bueno
        roe = datos.get('roe', 15)
        if roe >= 20:
            score += 15
        elif roe >= 15:
            score += 10
        elif roe >= 12:
            score += 5
        else:
            score -= 5
        
        # Deuda/Capital: <0.5 es bueno
        deuda = datos.get('deuda_capital', 0.5)
        if deuda < 0.3:
            score += 15
        elif deuda < 0.5:
            score += 10
        elif deuda < 0.7:
            score += 2
        else:
            score -= 10
        
        # Crecimiento ingresos: >5% es bueno
        crecimiento = datos.get('crecimiento_ingresos', 5)
        if crecimiento >= 10:
            score += 10
        elif crecimiento >= 7:
            score += 8
        elif crecimiento >= 5:
            score += 5
        else:
            score -= 5
        
        # Margen neto: >10% es bueno
        margen = datos.get('margen_neto', 8)
        if margen >= 15:
            score += 5
        elif margen >= 10:
            score += 3
        elif margen >= 5:
            score += 1
        
        return max(0, min(100, score))
    
    def analizar_salud_financiera(self, ticker):
        """Retorna estado de salud financiera con justificación."""
        datos = self.obtener_datos_empresa(ticker)
        if not datos:
            return {"salud": "Desconocida", "detalle": "Sin datos"}
        
        salud = datos.get('salud_financiera', 'Moderada')
        roe = datos.get('roe', 15)
        deuda = datos.get('deuda_capital', 0.5)
        crecimiento = datos.get('crecimiento_ingresos', 5)
        
        detalle = f"ROE: {roe}% | Deuda/Cap: {deuda:.2f} | Crecimiento: {crecimiento}%"
        
        return {
            "salud": salud,
            "detalle": detalle,
            "score": self.generar_score_fundamental(ticker)
        }

