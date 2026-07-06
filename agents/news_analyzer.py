"""news_analyzer.py — Análisis Avanzado de Noticias (con esteroides)
Captura noticias recientes, detecta relaciones entre empresas y genera contexto.

Mejora sobre la versión original: type hints en los métodos públicos, para
que el autocompletado y los checkers (mypy/pyright) detecten mal uso antes
de llegar a producción.
"""
from __future__ import annotations


class NewsAnalyzer:
    """Motor avanzado de análisis de noticias con relaciones."""

    NOTICIAS_DETALLADAS = {
        'ALICORC1.LM': [
            {
                'titulo': 'Alicorp reporta incremento de ventas en Q1 2024',
                'resumen': 'La empresa incremento sus ventas un 8.5% impulsada por expansion en lineas de consumo.',
                'fecha': 2, 'sentimiento': 0.75, 'fuente': 'Bloomberg Peru',
                'relacionadas': ['FERREYC1.LM', 'BBVAC1.LM'], 'impacto': 'alto'
            },
            {
                'titulo': 'Nuevas plantas de produccion aceleran crecimiento',
                'resumen': 'Alicorp abre dos nuevas plantas en provincias para llegar a mas ciudades.',
                'fecha': 5, 'sentimiento': 0.70, 'fuente': 'Gestion',
                'relacionadas': ['CPACASC1.LM'], 'impacto': 'medio'
            },
            {
                'titulo': 'Competencia presiona margenes pero Alicorp mantiene posicion',
                'resumen': 'A pesar de importaciones, Alicorp logra mantener cuota de mercado.',
                'fecha': 12, 'sentimiento': -0.30, 'fuente': 'Economia.pe',
                'relacionadas': ['FERREYC1.LM'], 'impacto': 'bajo'
            }
        ],
        'BBVAC1.LM': [
            {
                'titulo': 'BBVA Peru lidera crecimiento del sector bancario',
                'resumen': 'BBVA registra mayor crecimiento que competidores en colocaciones.',
                'fecha': 1, 'sentimiento': 0.85, 'fuente': 'SBS (Superintendencia)',
                'relacionadas': ['BAP', 'ALICORC1.LM'], 'impacto': 'alto'
            },
            {
                'titulo': 'Tasa de interes beneficia a bancos peruanos',
                'resumen': 'Subidas de tasas amplian margenes de intermediacion.',
                'fecha': 4, 'sentimiento': 0.75, 'fuente': 'BCR (Banco Central)',
                'relacionadas': ['BAP'], 'impacto': 'alto'
            },
            {
                'titulo': 'BBVA expande servicios digitales y fintech',
                'resumen': 'Lanzamiento de nuevas plataformas digitales atrae mas clientes jovenes.',
                'fecha': 8, 'sentimiento': 0.70, 'fuente': 'TechCrunch Peru',
                'relacionadas': [], 'impacto': 'medio'
            }
        ],
        'FERREYC1.LM': [
            {
                'titulo': 'Consumo de ferreteria se reactiva en 2024',
                'resumen': 'Proyectos inmobiliarios reactivados impulsan demanda de materiales.',
                'fecha': 3, 'sentimiento': 0.68, 'fuente': 'Capeco',
                'relacionadas': ['CPACASC1.LM', 'BAP'], 'impacto': 'alto'
            },
            {
                'titulo': 'Ferreycorp abre nuevas tiendas en Lima Metropolitana',
                'resumen': 'Expansion agresiva de sucursales en zonas de alto crecimiento.',
                'fecha': 6, 'sentimiento': 0.72, 'fuente': 'Gestion',
                'relacionadas': ['ALICORC1.LM'], 'impacto': 'medio'
            }
        ],
        'VOLCABC1.LM': [
            {
                'titulo': 'Precios del zinc y cobre al alza en mercados internacionales',
                'resumen': 'Commodities suben por recuperacion economica global.',
                'fecha': 2, 'sentimiento': 0.85, 'fuente': 'London Metal Exchange',
                'relacionadas': ['SCCO'], 'impacto': 'alto'
            },
            {
                'titulo': 'Volcan Minera aumenta produccion en respuesta a precios altos',
                'resumen': 'Productora de zinc anuncia incremento de output en 15%.',
                'fecha': 5, 'sentimiento': 0.80, 'fuente': 'Mining.com',
                'relacionadas': ['SCCO'], 'impacto': 'alto'
            },
            {
                'titulo': 'Demandas ambientales ralentizan expansion de Volcan',
                'resumen': 'Grupos ambientalistas se oponen a nuevo proyecto minero.',
                'fecha': 10, 'sentimiento': -0.65, 'fuente': 'Ecologia.pe',
                'relacionadas': [], 'impacto': 'medio'
            }
        ],
        'CPACASC1.LM': [
            {
                'titulo': 'Construccion se reactiva tras reduccion de tasas',
                'resumen': 'Sector inmobiliario muestra senales de recuperacion.',
                'fecha': 4, 'sentimiento': 0.65, 'fuente': 'INEI',
                'relacionadas': ['FERREYC1.LM', 'BAP'], 'impacto': 'alto'
            },
            {
                'titulo': 'Cementos Pacasmayo moderniza plantas de produccion',
                'resumen': 'Inversion en tecnologia verde reduce costos y emisiones.',
                'fecha': 7, 'sentimiento': 0.60, 'fuente': 'Construccion.pe',
                'relacionadas': ['ALICORC1.LM'], 'impacto': 'medio'
            }
        ],
        'SCCO': [
            {
                'titulo': 'Southern Copper obtiene record historico de ganancias',
                'resumen': 'Empresa minera reporta sus mejores resultados en 10 anos.',
                'fecha': 1, 'sentimiento': 0.90, 'fuente': 'Reuters',
                'relacionadas': ['VOLCABC1.LM'], 'impacto': 'alto'
            },
            {
                'titulo': 'Demanda global de cobre se fortalece por transicion energetica',
                'resumen': 'Energias renovables incrementan demanda de cobre para infraestructura.',
                'fecha': 3, 'sentimiento': 0.85, 'fuente': 'IEA',
                'relacionadas': ['VOLCABC1.LM'], 'impacto': 'alto'
            },
            {
                'titulo': 'Conflicto laboral afecta produccion de Southern Copper',
                'resumen': 'Huelga de empleados interrumpe operaciones por 3 semanas.',
                'fecha': 9, 'sentimiento': -0.70, 'fuente': 'Bloomberg',
                'relacionadas': [], 'impacto': 'alto'
            }
        ],
        'BAP': [
            {
                'titulo': 'Credicorp (BCP) lidera sector financiero peruano',
                'resumen': 'Mayor institucion financiera muestra solidez en resultados.',
                'fecha': 1, 'sentimiento': 0.80, 'fuente': 'BCRP',
                'relacionadas': ['BBVAC1.LM'], 'impacto': 'alto'
            },
            {
                'titulo': 'Confianza del consumidor en alza favorece creditos de BCP',
                'resumen': 'Colocaciones de credito crecen 9% en primeros meses del ano.',
                'fecha': 5, 'sentimiento': 0.75, 'fuente': 'BCRP',
                'relacionadas': ['ALICORC1.LM', 'FERREYC1.LM'], 'impacto': 'alto'
            }
        ]
    }

    def obtener_noticias_recientes(self, ticker: str, dias: int = 30) -> list[dict]:
        """Obtiene noticias recientes de un ticker."""
        noticias = self.NOTICIAS_DETALLADAS.get(ticker, [])
        return [n for n in noticias if n['fecha'] <= dias]

    def obtener_noticias_relacionadas(self, ticker: str) -> list[str]:
        """Obtiene noticias de empresas relacionadas."""
        noticias_propias = self.obtener_noticias_recientes(ticker)
        relacionadas = set()

        for noticia in noticias_propias:
            relacionadas.update(noticia.get('relacionadas', []))

        return list(relacionadas)

    def analizar_tendencia(self, ticker: str) -> dict:
        """Analiza la tendencia general de las noticias."""
        noticias = self.obtener_noticias_recientes(ticker)
        if not noticias:
            return {"tendencia": "neutra", "score": 0.0}

        score_promedio = sum(n['sentimiento'] for n in noticias) / len(noticias)

        if score_promedio >= 0.6:
            tendencia = "muy positiva"
        elif score_promedio >= 0.3:
            tendencia = "positiva"
        elif score_promedio >= -0.3:
            tendencia = "neutral"
        elif score_promedio >= -0.6:
            tendencia = "negativa"
        else:
            tendencia = "muy negativa"

        return {"tendencia": tendencia, "score": round(score_promedio, 2)}

    def generar_resumen_noticias(self, ticker: str) -> str:
        """Genera resumen narrativo de noticias."""
        noticias = self.obtener_noticias_recientes(ticker, dias=15)
        if not noticias:
            return "No hay noticias recientes disponibles."

        noticias_top = sorted(noticias, key=lambda x: x['fecha'])[:3]

        resumen = "Noticias recientes:\n"
        for noticia in noticias_top:
            resumen += f"\n- {noticia['titulo']}\n  {noticia['resumen']}\n"

        return resumen

    def detectar_catalistas(self, ticker: str) -> dict:
        """Detecta eventos catalizadores positivos y negativos."""
        noticias = self.obtener_noticias_recientes(ticker)

        positivos = [n for n in noticias if n['sentimiento'] > 0.5 and n['impacto'] in ['alto', 'medio']]
        negativos = [n for n in noticias if n['sentimiento'] < -0.5 and n['impacto'] in ['alto', 'medio']]

        return {
            "catalistas_positivos": positivos,
            "catalistas_negativos": negativos,
            "balance": len(positivos) - len(negativos)
        }