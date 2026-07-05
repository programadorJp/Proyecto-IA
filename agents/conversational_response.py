"""conversational_response.py — Generador de Respuestas Conversacionales

Crea respuestas naturales tipo humano usando análisis combinado."""

from datetime import datetime


class ConversationalResponseGenerator:
    """Genera respuestas conversacionales y naturales para inversiones."""
    
    def __init__(self):
        self.tonos = ["analista_experto", "asesor_amable", "inversor_experimentado"]
    
    def generar_analisis_conversacional(self, ticker, empresa, datos_completos):
        """
        Genera un análisis conversacional completo.
        datos_completos debe contener:
        - recomendacion (score + tipo)
        - noticias (resumen + tendencia)
        - predicciones (corto/mediano/largo plazo)
        - catalistas (positivos/negativos)
        """
        
        recomendacion = datos_completos.get('recomendacion', {})
        noticias = datos_completos.get('noticias', {})
        predicciones = datos_completos.get('predicciones', {})
        catalistas = datos_completos.get('catalistas', {})
        
        # Generar cada sección de manera conversacional
        seccion_bienvenida = self._generar_bienvenida(empresa, ticker)
        seccion_resumen_actual = self._generar_resumen_actual(empresa, recomendacion, noticias)
        seccion_noticias = self._generar_seccion_noticias(empresa, noticias)
        seccion_catalistas = self._generar_seccion_catalistas(empresa, catalistas)
        seccion_predicciones = self._generar_seccion_predicciones(empresa, predicciones)
        seccion_recomendacion_final = self._generar_recomendacion_final(empresa, recomendacion, predicciones)
        
        # Combinar todo
        respuesta_completa = f"""{seccion_bienvenida}

{seccion_resumen_actual}

{seccion_noticias}

{seccion_catalistas}

{seccion_predicciones}

{seccion_recomendacion_final}
"""
        return respuesta_completa.strip()
    
    def _generar_bienvenida(self, empresa, ticker):
        """Genera bienvenida conversacional."""
        return f"Hola, te presento mi análisis detallado de {empresa} ({ticker}).\n\nHeaquí lo que veo en el mercado ahora mismo:"
    
    def _generar_resumen_actual(self, empresa, recomendacion, noticias):
        """Genera resumen actual de la situación."""
        score = recomendacion.get('score_final', 50)
        rec_tipo = recomendacion.get('recomendacion', 'NEUTRAL')
        tendencia = noticias.get('tendencia', 'neutral')
        
        # Traducir score a palabras
        if score >= 80:
            sentimiento = "muy positivo, con vientos a favor"
        elif score >= 70:
            sentimiento = "positivo, con buenas perspectivas"
        elif score >= 60:
            sentimiento = "moderadamente positivo"
        elif score >= 50:
            sentimiento = "neutral, sin tendencia clara"
        elif score >= 40:
            sentimiento = "algo preocupante, con señales mixtas"
        else:
            sentimiento = "negativo, con desafíos por delante"
        
        resumen = f"""PANORAMA ACTUAL:
En este momento, {empresa} se ve {sentimiento}. El mercado le asigna 
un score de {score}/100, lo que sugiere una recomendación de {rec_tipo}.

Las noticias recientes pintan un cuadro {tendencia} alrededor de la empresa.
Esto es importante porque refuerza o contradice lo que vemos en los números."""
        
        return resumen
    
    def _generar_seccion_noticias(self, empresa, noticias):
        """Genera sección sobre noticias."""
        resumen_noticias = noticias.get('resumen', '')
        tendencia = noticias.get('tendencia', 'neutral')
        
        if tendencia == "muy positiva":
            tono = "Las noticias son muy alentadoras"
        elif tendencia == "positiva":
            tono = "Las noticias son generalmente positivas"
        elif tendencia == "neutral":
            tono = "Las noticias son mixtas, sin un patrón claro"
        elif tendencia == "negativa":
            tono = "Las noticias son preocupantes"
        else:
            tono = "Las noticias son muy negativas"
        
        seccion = f"""\n¿CUAL ES LA NOTICIA?
{tono}. Aquí está lo que está pasando:

{resumen_noticias}

Esto importa porque refleja la realidad del negocio: si las noticias son 
positivas, probablemente el precio subirá en el futuro."""
        
        return seccion
    
    def _generar_seccion_catalistas(self, empresa, catalistas):
        """Genera sección sobre catalizadores."""
        positivos = catalistas.get('catalistas_positivos', [])
        negativos = catalistas.get('catalistas_negativos', [])
        
        seccion = "\nTENGAS EN CUENTA ESTO (Catalistas):\n"
        
        if positivos:
            seccion += "\nA FAVOR de {}: \n".format(empresa)
            for cat in positivos[:2]:
                seccion += f"- {cat.get('titulo', 'Evento positivo')}\n"
        
        if negativos:
            seccion += "\nEN CONTRA de {}: \n".format(empresa)
            for cat in negativos[:2]:
                seccion += f"- {cat.get('titulo', 'Evento negativo')}\n"
        
        if not positivos and not negativos:
            seccion += "No hay catalistas claros en el corto plazo."
        
        return seccion
    
    def _generar_seccion_predicciones(self, empresa, predicciones):
        """Genera sección sobre predicciones futuras."""
        
        pred_corto = predicciones.get('corto_plazo', {})
        pred_mediano = predicciones.get('mediano_plazo', {})
        pred_largo = predicciones.get('largo_plazo', {})
        escenarios = predicciones.get('escenarios', {})
        
        seccion = f"""\nMIS PREDICCIONES PARA {empresa.upper()}:

1. CORTO PLAZO (próximas 4 semanas):
   Espero que {pred_corto.get('direccion', 'se mantenga').lower()}
   Confianza: {pred_corto.get('confianza', 'media')}

2. MEDIANO PLAZO (3-6 meses):
   Tendencia: {pred_mediano.get('direccion', 'neutral').lower()}
   Expectativa: {pred_mediano.get('prediccion_score', 50)}/100

3. LARGO PLAZO (1+ anos):
   Potencial de largo plazo: {pred_largo.get('potencial', 'moderado')}
   Mi outlook: {pred_largo.get('outlook', 'Mantener y monitorear')}

ESCENARIOS DE PRECIO:
"""
        if escenarios:
            sec = escenarios
            seccion += f"""
- Escenario BAJISTA (20% probabilidad): 
  Precio esperado: S/. {sec['escenario_bajista']['precio_esperado']}
  ({sec['escenario_bajista']['cambio_porcentaje']:+.2f}%)

- Escenario BASE (60% probabilidad): 
  Precio esperado: S/. {sec['escenario_base']['precio_esperado']}
  ({sec['escenario_base']['cambio_porcentaje']:+.2f}%)
  
- Escenario ALCISTA (20% probabilidad): 
  Precio esperado: S/. {sec['escenario_alcista']['precio_esperado']}
  ({sec['escenario_alcista']['cambio_porcentaje']:+.2f}%)
"""
        
        return seccion
    
    def _generar_recomendacion_final(self, empresa, recomendacion, predicciones):
        """Genera recomendación final conversacional."""
        
        rec_tipo = recomendacion.get('recomendacion', 'NEUTRAL')
        score = recomendacion.get('score_final', 50)
        
        # Generar argumentación
        if score >= 80:
            argumento = f"""{empresa} es una COMPRA FUERTE. Los números son sólidos, 
las noticias son positivas, y las predicciones sugieren crecimiento. 
Si tienes perfil de riesgo moderado a agresivo, esta es una oportunidad."""
        elif score >= 70:
            argumento = f"""{empresa} es una BUENA COMPRA. Tiene fundamentales sólidos 
y noticias positivas. Recomendado para inversores dispuestos a esperar 
resultados en los próximos meses."""
        elif score >= 55:
            argumento = f"""{empresa} vale la pena MANTENER. No es un "no comprar", 
pero tampoco es momento de agregar posiciones. Espera señales más claras."""
        elif score >= 40:
            argumento = f"""Sugiero VENDER o no entrar en {empresa}. Las señales son 
negativas y hay mejores oportunidades en el mercado."""
        else:
            argumento = f"""Evita {empresa} por ahora. El outlook es negativo y 
el riesgo/recompensa no justifica la inversión en este momento."""
        
        seccion = f"""\nMI RECOMENDACIÓN FINAL:

{argumento}

SCORE FINAL: {score}/100 → {rec_tipo}

Disclaimer: Este análisis es informativo. Consulta con un asesor 
financiero certificado antes de tomar decisiones de inversión. 
Los mercados son impredecibles y el pasado no garantiza el futuro.
"""
        
        return seccion
    
    def generar_respuesta_rapida(self, ticker, empresa, score_final, recomendacion):
        """Genera una respuesta rápida de una línea."""
        if score_final >= 75:
            return f"{empresa}: Es momento de COMPRAR. Score {score_final}/100. Buenas noticias y potencial al alza."
        elif score_final >= 65:
            return f"{empresa}: COMPRA recomendada. Score {score_final}/100. Fundamentales positivos."
        elif score_final >= 55:
            return f"{empresa}: MANTÉN tu posición. Score {score_final}/100. Neutral, espera claridad."
        elif score_final >= 40:
            return f"{empresa}: Considera VENDER. Score {score_final}/100. Señales negativas."
        else:
            return f"{empresa}: EVITA por ahora. Score {score_final}/100. Outlook muy negativo."

