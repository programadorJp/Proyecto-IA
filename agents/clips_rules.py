"""clips_rules.py — Motor de Reglas estilo CLIPS (con esteroides)
Sistema Experto BVL · UPAO 2026
Implementa un sistema de producción IF-THEN con encadenamiento hacia adelante (forward chaining) para evaluar activos financieros.
Total de reglas: 90 reglas organizadas en 8 categorías

Mejoras sobre la versión original:
- Nuevos métodos de consulta: get_regla_por_id(), reglas_por_categoria(),
  listar_categorias() — útiles para debugging y para un futuro endpoint
  "/reglas/catalogo" que muestre el motor completo sin tener que evaluar
  un DataFrame.
- El "except Exception: continue" que silenciaba errores de una regla mal
  formada ahora al menos loggea qué regla falló y por qué, en vez de fallar
  en silencio total (antes era imposible saber si una regla nunca disparaba
  por su lógica o porque estaba reventando).
- Índice interno por categoría (se construye una vez en __init__) para que
  reglas_por_categoria() no tenga que recorrer las 90 reglas cada vez.
"""
import logging

logger = logging.getLogger(__name__)


class ClipsRulesEngine:
    """Motor de inferencia hacia adelante.
    Categorías de reglas:
    R01-R10  → Señales de crecimiento
    R11-R20  → Señales de caída
    R21-R30  → Perfil Conservador
    R31-R40  → Perfil Moderado
    R41-R50  → Perfil Agresivo
    R51-R60  → Análisis de precio
    R61-R70  → Sectores y fuentes
    R71-R80  → Reglas combinadas
    R81-R90  → Alertas y advertencias"""

    REGLAS = [

        # CATEGORÍA 1: SEÑALES DE CRECIMIENTO (R01-R10)
        {
            "id": "R01", "categoria": "Crecimiento",
            "nombre": "MOMENTUM_FUERTE_POSITIVO",
            "condicion": lambda f, p: f["Crecimiento_%"] >= 5.0,
            "accion": "COMPRA FUERTE — Momentum alcista excepcional, señal muy positiva",
            "icono": "🚀", "color": "#00e5a0", "prioridad": 1
        },
        {
            "id": "R02", "categoria": "Crecimiento",
            "nombre": "MOMENTUM_MODERADO_POSITIVO",
            "condicion": lambda f, p: 3.0 <= f["Crecimiento_%"] < 5.0,
            "accion": "COMPRAR — Momentum alcista fuerte detectado",
            "icono": "📈", "color": "#00e5a0", "prioridad": 2
        },
        {
            "id": "R03", "categoria": "Crecimiento",
            "nombre": "CRECIMIENTO_LEVE",
            "condicion": lambda f, p: 1.0 <= f["Crecimiento_%"] < 3.0,
            "accion": "CONSIDERAR COMPRA — Crecimiento leve, tendencia positiva",
            "icono": "📊", "color": "#4ecdc4", "prioridad": 3
        },
        {
            "id": "R04", "categoria": "Crecimiento",
            "nombre": "CRECIMIENTO_MINIMO",
            "condicion": lambda f, p: 0.0 < f["Crecimiento_%"] < 1.0,
            "accion": "MANTENER — Crecimiento mínimo, posición estable",
            "icono": "➡️", "color": "#6c7a95", "prioridad": 4
        },
        {
            "id": "R05", "categoria": "Crecimiento",
            "nombre": "CRECIMIENTO_EXCEPCIONAL",
            "condicion": lambda f, p: f["Crecimiento_%"] >= 8.0,
            "accion": "ALERTA POSITIVA — Crecimiento excepcional, verificar noticias corporativas",
            "icono": "⭐", "color": "#ffd700", "prioridad": 1
        },
        {
            "id": "R06", "categoria": "Crecimiento",
            "nombre": "RECUPERACION_TECNICA",
            "condicion": lambda f, p: 2.0 <= f["Crecimiento_%"] < 4.0 and f["Precio"] < 10.0,
            "accion": "OPORTUNIDAD — Posible recuperación técnica en precio bajo",
            "icono": "🔄", "color": "#4ecdc4", "prioridad": 3
        },
        {
            "id": "R07", "categoria": "Crecimiento",
            "nombre": "CRECIMIENTO_CON_PRECIO_ALTO",
            "condicion": lambda f, p: f["Crecimiento_%"] >= 2.0 and f["Precio"] >= 100.0,
            "accion": "MANTENER POSICION — Activo premium con buen momentum",
            "icono": "💎", "color": "#00e5a0", "prioridad": 2
        },
        {
            "id": "R08", "categoria": "Crecimiento",
            "nombre": "REBOTE_RAPIDO",
            "condicion": lambda f, p: f["Crecimiento_%"] >= 4.0 and f["Precio"] < 5.0,
            "accion": "ESPECULAR — Rebote rápido en penny stock, alto riesgo/retorno",
            "icono": "⚡", "color": "#ffd700", "prioridad": 2
        },
        {
            "id": "R09", "categoria": "Crecimiento",
            "nombre": "TENDENCIA_ALCISTA_MINERIA",
            "condicion": lambda f, p: f["Crecimiento_%"] >= 1.5 and "Copper" in f["Empresa"],
            "accion": "COMPRAR — Minería con tendencia alcista, beneficio por precios de commodities",
            "icono": "⛏️", "color": "#00e5a0", "prioridad": 2
        },
        {
            "id": "R10", "categoria": "Crecimiento",
            "nombre": "TENDENCIA_ALCISTA_BANCARIA",
            "condicion": lambda f, p: f["Crecimiento_%"] >= 1.0 and any(b in f["Empresa"] for b in ["BBVA","BCP","Credicorp"]),
            "accion": "COMPRAR — Sector bancario con crecimiento, respaldo sólido",
            "icono": "🏦", "color": "#00e5a0", "prioridad": 2
        },

        # CATEGORÍA 2: SEÑALES DE CAÍDA (R11-R20)
        {
            "id": "R11", "categoria": "Caída",
            "nombre": "CAIDA_CRITICA",
            "condicion": lambda f, p: f["Crecimiento_%"] <= -5.0,
            "accion": "VENDER URGENTE — Caída crítica, activa stop-loss inmediatamente",
            "icono": "🔴", "color": "#ff4757", "prioridad": 1
        },
        {
            "id": "R12", "categoria": "Caída",
            "nombre": "CAIDA_FUERTE",
            "condicion": lambda f, p: -5.0 < f["Crecimiento_%"] <= -3.0,
            "accion": "VENDER / STOP-LOSS — Caída fuerte, revisar posición urgente",
            "icono": "📉", "color": "#ff4757", "prioridad": 1
        },
        {
            "id": "R13", "categoria": "Caída",
            "nombre": "CAIDA_MODERADA",
            "condicion": lambda f, p: -3.0 < f["Crecimiento_%"] <= -1.5,
            "accion": "PRECAUCIÓN — Caída moderada, monitorear de cerca",
            "icono": "⚠️", "color": "#ff6b35", "prioridad": 2
        },
        {
            "id": "R14", "categoria": "Caída",
            "nombre": "CAIDA_LEVE",
            "condicion": lambda f, p: -1.5 < f["Crecimiento_%"] <= -0.5,
            "accion": "OBSERVAR — Caída leve, puede ser corrección normal",
            "icono": "👁️", "color": "#6c7a95", "prioridad": 3
        },
        {
            "id": "R15", "categoria": "Caída",
            "nombre": "CAIDA_PRECIO_BAJO",
            "condicion": lambda f, p: f["Crecimiento_%"] <= -2.0 and f["Precio"] < 2.0,
            "accion": "ALERTA ROJA — Activo de bajo precio en caída, riesgo de desvalorización",
            "icono": "🚨", "color": "#ff4757", "prioridad": 1
        },
        {
            "id": "R16", "categoria": "Caída",
            "nombre": "CAIDA_PRECIO_ALTO",
            "condicion": lambda f, p: f["Crecimiento_%"] <= -3.0 and f["Precio"] >= 50.0,
            "accion": "REVISAR PORTAFOLIO — Activo premium en caída, posible ajuste sectorial",
            "icono": "📊", "color": "#ff6b35", "prioridad": 2
        },
        {
            "id": "R17", "categoria": "Caída",
            "nombre": "CAIDA_SECTOR_MINERO",
            "condicion": lambda f, p: f["Crecimiento_%"] <= -2.0 and any(m in f["Empresa"] for m in ["Volcan","Southern","Copper"]),
            "accion": "PRECAUCIÓN MINERÍA — Caída en sector minero, revisar precios de metales",
            "icono": "⛏️", "color": "#ff6b35", "prioridad": 2
        },
        {
            "id": "R18", "categoria": "Caída",
            "nombre": "CAIDA_SECTOR_CONSTRUCCION",
            "condicion": lambda f, p: f["Crecimiento_%"] <= -2.0 and "Pacasmayo" in f["Empresa"],
            "accion": "PRECAUCIÓN CONSTRUCCIÓN — Sector sensible a ciclos económicos peruanos",
            "icono": "🏗️", "color": "#ff6b35", "prioridad": 2
        },
        {
            "id": "R19", "categoria": "Caída",
            "nombre": "CAIDA_CON_REBOTE_POSIBLE",
            "condicion": lambda f, p: -4.0 < f["Crecimiento_%"] <= -2.0 and p == "Agresivo",
            "accion": "OPORTUNIDAD CONTRARIAN — Caída puede ser entrada para perfil agresivo",
            "icono": "🎯", "color": "#3b82f6", "prioridad": 3
        },
        {
            "id": "R20", "categoria": "Caída",
            "nombre": "ZONA_SOPORTE",
            "condicion": lambda f, p: -1.0 < f["Crecimiento_%"] <= 0.0,
            "accion": "ZONA NEUTRAL — Precio en soporte, esperar confirmación de tendencia",
            "icono": "⚖️", "color": "#6c7a95", "prioridad": 4
        },

        # CATEGORÍA 3: PERFIL CONSERVADOR (R21-R30)
        {
            "id": "R21", "categoria": "Conservador",
            "nombre": "CONSERVADOR_ZONA_IDEAL",
            "condicion": lambda f, p: p == "Conservador" and -0.5 <= f["Crecimiento_%"] <= 1.5,
            "accion": "IDEAL CONSERVADOR — Activo estable, bajo riesgo, apto para portafolio conservador",
            "icono": "🛡️", "color": "#4ecdc4", "prioridad": 2
        },
        {
            "id": "R22", "categoria": "Conservador",
            "nombre": "CONSERVADOR_BANCO_SEGURO",
            "condicion": lambda f, p: p == "Conservador" and any(b in f["Empresa"] for b in ["BBVA","BCP","Credicorp"]) and f["Crecimiento_%"] >= 0,
            "accion": "RECOMENDADO — Banco sólido con rendimiento positivo, bajo riesgo sistémico",
            "icono": "🏦", "color": "#4ecdc4", "prioridad": 2
        },
        {
            "id": "R23", "categoria": "Conservador",
            "nombre": "CONSERVADOR_EVITAR_VOLATIL",
            "condicion": lambda f, p: p == "Conservador" and abs(f["Crecimiento_%"]) > 3.0,
            "accion": "NO RECOMENDADO — Alta volatilidad, incompatible con perfil conservador",
            "icono": "🚫", "color": "#ff6b35", "prioridad": 2
        },
        {
            "id": "R24", "categoria": "Conservador",
            "nombre": "CONSERVADOR_PRECIO_ESTABLE",
            "condicion": lambda f, p: p == "Conservador" and f["Precio"] >= 5.0 and abs(f["Crecimiento_%"]) <= 1.0,
            "accion": "MANTENER — Precio estable y suficiente, ideal para conservador",
            "icono": "✅", "color": "#4ecdc4", "prioridad": 3
        },
        {
            "id": "R25", "categoria": "Conservador",
            "nombre": "CONSERVADOR_MINERIA_RIESGO",
            "condicion": lambda f, p: p == "Conservador" and any(m in f["Empresa"] for m in ["Volcan","Southern","Copper"]),
            "accion": "PRECAUCIÓN — Minería es volátil, no ideal para perfil conservador",
            "icono": "⚠️", "color": "#ff6b35", "prioridad": 2
        },
        {
            "id": "R26", "categoria": "Conservador",
            "nombre": "CONSERVADOR_ALICORP_SEGURO",
            "condicion": lambda f, p: p == "Conservador" and "Alicorp" in f["Empresa"] and f["Crecimiento_%"] >= 0,
            "accion": "RECOMENDADO — Consumo masivo estable, defensivo en recesión",
            "icono": "🛡️", "color": "#4ecdc4", "prioridad": 2
        },
        {
            "id": "R27", "categoria": "Conservador",
            "nombre": "CONSERVADOR_DIVIDENDO_POTENCIAL",
            "condicion": lambda f, p: p == "Conservador" and f["Precio"] >= 20.0 and f["Crecimiento_%"] >= 0.5,
            "accion": "POTENCIAL DIVIDENDO — Empresa madura con posible reparto de dividendos",
            "icono": "💰", "color": "#ffd700", "prioridad": 3
        },
        {
            "id": "R28", "categoria": "Conservador",
            "nombre": "CONSERVADOR_CAIDA_SALIR",
            "condicion": lambda f, p: p == "Conservador" and f["Crecimiento_%"] <= -2.0,
            "accion": "SALIR — Perfil conservador no debe tolerar esta caída",
            "icono": "🚪", "color": "#ff4757", "prioridad": 1
        },
        {
            "id": "R29", "categoria": "Conservador",
            "nombre": "CONSERVADOR_FERREYCORP",
            "condicion": lambda f, p: p == "Conservador" and "Ferreycorp" in f["Empresa"] and f["Crecimiento_%"] >= 0,
            "accion": "CONSIDERAR — Ferreycorp es empresa industrial estable en Perú",
            "icono": "🔧", "color": "#4ecdc4", "prioridad": 3
        },
        {
            "id": "R30", "categoria": "Conservador",
            "nombre": "CONSERVADOR_PRECIO_MUY_BAJO",
            "condicion": lambda f, p: p == "Conservador" and f["Precio"] < 1.0,
            "accion": "EVITAR — Precio demasiado bajo para perfil conservador, alto riesgo",
            "icono": "❌", "color": "#ff4757", "prioridad": 2
        },

        # CATEGORÍA 4: PERFIL MODERADO (R31-R40)
        {
            "id": "R31", "categoria": "Moderado",
            "nombre": "MODERADO_ZONA_OPTIMA",
            "condicion": lambda f, p: p == "Moderado" and 1.0 <= f["Crecimiento_%"] <= 4.0,
            "accion": "ZONA ÓPTIMA — Crecimiento moderado ideal para este perfil",
            "icono": "⚖️", "color": "#4ecdc4", "prioridad": 2
        },
        {
            "id": "R32", "categoria": "Moderado",
            "nombre": "MODERADO_DIVERSIFICAR",
            "condicion": lambda f, p: p == "Moderado" and 0.0 <= f["Crecimiento_%"] < 1.0,
            "accion": "MANTENER Y DIVERSIFICAR — Bajo crecimiento, considerar complementar portafolio",
            "icono": "📋", "color": "#6c7a95", "prioridad": 3
        },
        {
            "id": "R33", "categoria": "Moderado",
            "nombre": "MODERADO_CRECIMIENTO_ALTO",
            "condicion": lambda f, p: p == "Moderado" and f["Crecimiento_%"] > 4.0,
            "accion": "REVISAR RIESGO — Crecimiento alto puede implicar mayor volatilidad futura",
            "icono": "🔍", "color": "#ffd700", "prioridad": 2
        },
        {
            "id": "R34", "categoria": "Moderado",
            "nombre": "MODERADO_CAIDA_ACEPTABLE",
            "condicion": lambda f, p: p == "Moderado" and -2.0 <= f["Crecimiento_%"] < 0.0,
            "accion": "TOLERABLE — Caída dentro del rango aceptable para perfil moderado",
            "icono": "📊", "color": "#6c7a95", "prioridad": 3
        },
        {
            "id": "R35", "categoria": "Moderado",
            "nombre": "MODERADO_CAIDA_LIMITE",
            "condicion": lambda f, p: p == "Moderado" and f["Crecimiento_%"] < -2.0,
            "accion": "LÍMITE MODERADO — Caída supera tolerancia, considerar reducir posición",
            "icono": "⚠️", "color": "#ff6b35", "prioridad": 2
        },
        {
            "id": "R36", "categoria": "Moderado",
            "nombre": "MODERADO_BVL_REAL_TIME",
            "condicion": lambda f, p: p == "Moderado" and f["Sector"] == "BVL Real-Time" and f["Crecimiento_%"] >= 0.5,
            "accion": "DATO CONFIABLE — Precio en tiempo real con tendencia positiva",
            "icono": "📡", "color": "#4ecdc4", "prioridad": 3
        },
        {
            "id": "R37", "categoria": "Moderado",
            "nombre": "MODERADO_CREDICORP",
            "condicion": lambda f, p: p == "Moderado" and "Credicorp" in f["Empresa"],
            "accion": "RECOMENDADO — Credicorp es líder financiero peruano, bajo riesgo relativo",
            "icono": "🏛️", "color": "#4ecdc4", "prioridad": 2
        },
        {
            "id": "R38", "categoria": "Moderado",
            "nombre": "MODERADO_SOUTHERN_COPPER",
            "condicion": lambda f, p: p == "Moderado" and "Southern" in f["Empresa"] and f["Crecimiento_%"] >= 0,
            "accion": "CONSIDERAR — Southern Copper tiene exposición internacional, diversifica geográficamente",
            "icono": "🌍", "color": "#4ecdc4", "prioridad": 3
        },
        {
            "id": "R39", "categoria": "Moderado",
            "nombre": "MODERADO_BALANCE_PORTAFOLIO",
            "condicion": lambda f, p: p == "Moderado" and f["Precio"] >= 10.0 and 0 <= f["Crecimiento_%"] <= 3.0,
            "accion": "BALANCE IDEAL — Precio y crecimiento equilibrados para portafolio moderado",
            "icono": "⚖️", "color": "#00e5a0", "prioridad": 2
        },
        {
            "id": "R40", "categoria": "Moderado",
            "nombre": "MODERADO_VOLATILIDAD_EXTREMA",
            "condicion": lambda f, p: p == "Moderado" and abs(f["Crecimiento_%"]) > 5.0,
            "accion": "ALTA VOLATILIDAD — Supera tolerancia moderada, reducir exposición",
            "icono": "🌊", "color": "#ff6b35", "prioridad": 2
        },

        # CATEGORÍA 5: PERFIL AGRESIVO (R41-R50)
        {
            "id": "R41", "categoria": "Agresivo",
            "nombre": "AGRESIVO_MAXIMO_RETORNO",
            "condicion": lambda f, p: p == "Agresivo" and f["Crecimiento_%"] >= 5.0,
            "accion": "ENTRADA AGRESIVA — Máximo momentum, aprovechar tendencia alcista",
            "icono": "🚀", "color": "#00e5a0", "prioridad": 1
        },
        {
            "id": "R42", "categoria": "Agresivo",
            "nombre": "AGRESIVO_PENNY_STOCK",
            "condicion": lambda f, p: p == "Agresivo" and f["Precio"] < 1.0 and f["Crecimiento_%"] >= 0,
            "accion": "ESPECULAR — Penny stock con potencial de multiplicar, alto riesgo aceptado",
            "icono": "🎰", "color": "#a855f7", "prioridad": 2
        },
        {
            "id": "R43", "categoria": "Agresivo",
            "nombre": "AGRESIVO_MINERIA_OPORTUNIDAD",
            "condicion": lambda f, p: p == "Agresivo" and any(m in f["Empresa"] for m in ["Volcan","Southern","Copper"]) and f["Crecimiento_%"] >= 0,
            "accion": "OPORTUNIDAD MINERA — Sector volátil apto para perfil agresivo, alto potencial",
            "icono": "⛏️", "color": "#ffd700", "prioridad": 2
        },
        {
            "id": "R44", "categoria": "Agresivo",
            "nombre": "AGRESIVO_CAIDA_ENTRADA",
            "condicion": lambda f, p: p == "Agresivo" and -5.0 < f["Crecimiento_%"] <= -2.0,
            "accion": "COMPRA EN CAÍDA — Estrategia contrarian, posible rebote técnico",
            "icono": "🎯", "color": "#3b82f6", "prioridad": 2
        },
        {
            "id": "R45", "categoria": "Agresivo",
            "nombre": "AGRESIVO_STOP_LOSS_EXTREMO",
            "condicion": lambda f, p: p == "Agresivo" and f["Crecimiento_%"] <= -5.0,
            "accion": "STOP-LOSS — Incluso perfil agresivo debe protegerse ante caída extrema",
            "icono": "🛑", "color": "#ff4757", "prioridad": 1
        },
        {
            "id": "R46", "categoria": "Agresivo",
            "nombre": "AGRESIVO_PRECIO_BAJO_POTENCIAL",
            "condicion": lambda f, p: p == "Agresivo" and f["Precio"] < 3.0 and f["Crecimiento_%"] > 0,
            "accion": "ALTO POTENCIAL — Precio bajo con crecimiento, multiplicador posible",
            "icono": "💥", "color": "#ffd700", "prioridad": 2
        },
        {
            "id": "R47", "categoria": "Agresivo",
            "nombre": "AGRESIVO_VOLCAN_MINERA",
            "condicion": lambda f, p: p == "Agresivo" and "Volcan" in f["Empresa"],
            "accion": "ESPECULATIVO — Volcan Minera alta volatilidad, oportunidad para agresivos",
            "icono": "🌋", "color": "#a855f7", "prioridad": 2
        },
        {
            "id": "R48", "categoria": "Agresivo",
            "nombre": "AGRESIVO_DIVERSIFICAR_RIESGO",
            "condicion": lambda f, p: p == "Agresivo" and f["Crecimiento_%"] >= 3.0,
            "accion": "CONCENTRAR POSICIÓN — Buen momentum, considera aumentar posición gradualmente",
            "icono": "📈", "color": "#00e5a0", "prioridad": 2
        },
        {
            "id": "R49", "categoria": "Agresivo",
            "nombre": "AGRESIVO_INTERNACIONAL",
            "condicion": lambda f, p: p == "Agresivo" and f["Ticker"] in ["BAP", "SCCO"],
            "accion": "EXPOSICIÓN INTERNACIONAL — Ticker en NYSE, diversificación global para agresivo",
            "icono": "🌐", "color": "#4ecdc4", "prioridad": 3
        },
        {
            "id": "R50", "categoria": "Agresivo",
            "nombre": "AGRESIVO_ZONA_NEUTRAL_ESPERAR",
            "condicion": lambda f, p: p == "Agresivo" and -1.0 <= f["Crecimiento_%"] <= 0.5,
            "accion": "ESPERAR SEÑAL — Zona neutral, aguardar momentum claro antes de entrar",
            "icono": "⏳", "color": "#6c7a95", "prioridad": 4
        },

        # CATEGORÍA 6: ANÁLISIS DE PRECIO (R51-R60)
        {
            "id": "R51", "categoria": "Precio",
            "nombre": "PRECIO_PREMIUM",
            "condicion": lambda f, p: f["Precio"] >= 100.0,
            "accion": "ACTIVO PREMIUM — Precio elevado, empresa de gran capitalización",
            "icono": "💎", "color": "#ffd700", "prioridad": 3
        },
        {
            "id": "R52", "categoria": "Precio",
            "nombre": "PRECIO_ALTO",
            "condicion": lambda f, p: 50.0 <= f["Precio"] < 100.0,
            "accion": "PRECIO ALTO — Empresa mediana-grande, mayor estabilidad relativa",
            "icono": "📊", "color": "#4ecdc4", "prioridad": 4
        },
        {
            "id": "R53", "categoria": "Precio",
            "nombre": "PRECIO_MEDIO",
            "condicion": lambda f, p: 10.0 <= f["Precio"] < 50.0,
            "accion": "PRECIO MEDIO — Rango accesible, buena liquidez típicamente",
            "icono": "⚖️", "color": "#6c7a95", "prioridad": 4
        },
        {
            "id": "R54", "categoria": "Precio",
            "nombre": "PRECIO_BAJO",
            "condicion": lambda f, p: 2.0 <= f["Precio"] < 10.0,
            "accion": "PRECIO BAJO — Mayor volatilidad porcentual, monitorear con atención",
            "icono": "⚠️", "color": "#ff6b35", "prioridad": 4
        },
        {
            "id": "R55", "categoria": "Precio",
            "nombre": "PRECIO_MUY_BAJO",
            "condicion": lambda f, p: f["Precio"] < 2.0,
            "accion": "PRECIO MUY BAJO — Alta especulación, solo para perfiles agresivos informados",
            "icono": "🎲", "color": "#a855f7", "prioridad": 3
        },
        {
            "id": "R56", "categoria": "Precio",
            "nombre": "PRECIO_PREMIUM_EN_CAIDA",
            "condicion": lambda f, p: f["Precio"] >= 100.0 and f["Crecimiento_%"] <= -2.0,
            "accion": "REVISIÓN URGENTE — Empresa premium en caída, verificar fundamentales",
            "icono": "🔍", "color": "#ff6b35", "prioridad": 2
        },
        {
            "id": "R57", "categoria": "Precio",
            "nombre": "PRECIO_BAJO_EN_ALZA",
            "condicion": lambda f, p: f["Precio"] < 5.0 and f["Crecimiento_%"] >= 3.0,
            "accion": "POTENCIAL ALCISTA — Precio bajo con momentum, vigilar volumen",
            "icono": "🚀", "color": "#ffd700", "prioridad": 2
        },
        {
            "id": "R58", "categoria": "Precio",
            "nombre": "PRECIO_CREDICORP_REFERENCIA",
            "condicion": lambda f, p: "Credicorp" in f["Empresa"] and f["Precio"] >= 150.0,
            "accion": "CREDICORP PREMIUM — Precio histórico alto, empresa líder BVL y NYSE",
            "icono": "🏛️", "color": "#4ecdc4", "prioridad": 3
        },
        {
            "id": "R59", "categoria": "Precio",
            "nombre": "PRECIO_SOUTHERN_REFERENCIA",
            "condicion": lambda f, p: "Southern" in f["Empresa"] and f["Precio"] >= 80.0,
            "accion": "SOUTHERN PREMIUM — Cotización en NYSE, benchmark de minería cuprífera global",
            "icono": "🌎", "color": "#4ecdc4", "prioridad": 3
        },
        {
            "id": "R60", "categoria": "Precio",
            "nombre": "RELACION_PRECIO_CRECIMIENTO",
            "condicion": lambda f, p: f["Precio"] > 0 and f["Crecimiento_%"] / max(f["Precio"], 1) > 0.1,
            "accion": "RATIO FAVORABLE — Crecimiento proporcional al precio es positivo",
            "icono": "📐", "color": "#00e5a0", "prioridad": 3
        },

        # CATEGORÍA 7: SECTORES Y FUENTES (R61-R70)
        {
            "id": "R61", "categoria": "Sector",
            "nombre": "DATO_TIEMPO_REAL",
            "condicion": lambda f, p: f["Sector"] == "BVL Real-Time",
            "accion": "DATO CONFIABLE — Precio obtenido en tiempo real desde yfinance",
            "icono": "📡", "color": "#00e5a0", "prioridad": 5
        },
        {
            "id": "R62", "categoria": "Sector",
            "nombre": "DATO_DEMO",
            "condicion": lambda f, p: f["Sector"] in ("Demo", "Demo BVL"),
            "accion": "DATO REFERENCIAL — Precio de referencia, verificar con fuente oficial",
            "icono": "ℹ️", "color": "#6c7a95", "prioridad": 5
        },
        {
            "id": "R63", "categoria": "Sector",
            "nombre": "DATO_OFFLINE",
            "condicion": lambda f, p: f["Sector"] == "Offline",
            "accion": "SIN CONEXIÓN — Datos no actualizados, decisiones con precaución",
            "icono": "📵", "color": "#ff6b35", "prioridad": 4
        },
        {
            "id": "R64", "categoria": "Sector",
            "nombre": "SECTOR_FINANCIERO",
            "condicion": lambda f, p: any(b in f["Empresa"] for b in ["BBVA","BCP","Credicorp"]),
            "accion": "SECTOR FINANCIERO — Regulado por SBS, alta transparencia normativa",
            "icono": "🏦", "color": "#4ecdc4", "prioridad": 5
        },
        {
            "id": "R65", "categoria": "Sector",
            "nombre": "SECTOR_CONSUMO_MASIVO",
            "condicion": lambda f, p: "Alicorp" in f["Empresa"],
            "accion": "SECTOR CONSUMO — Defensivo ante recesión, demanda inelástica en Perú",
            "icono": "🛒", "color": "#4ecdc4", "prioridad": 5
        },
        {
            "id": "R66", "categoria": "Sector",
            "nombre": "SECTOR_MINERIA",
            "condicion": lambda f, p: any(m in f["Empresa"] for m in ["Volcan","Southern","Copper"]),
            "accion": "SECTOR MINERO — Correlacionado con precios de metales internacionales",
            "icono": "⛏️", "color": "#ff6b35", "prioridad": 5
        },
        {
            "id": "R67", "categoria": "Sector",
            "nombre": "SECTOR_CONSTRUCCION",
            "condicion": lambda f, p: "Pacasmayo" in f["Empresa"],
            "accion": "SECTOR CONSTRUCCIÓN — Sensible a inversión pública peruana e infraestructura",
            "icono": "🏗️", "color": "#ff6b35", "prioridad": 5
        },
        {
            "id": "R68", "categoria": "Sector",
            "nombre": "SECTOR_INDUSTRIAL",
            "condicion": lambda f, p: "Ferreycorp" in f["Empresa"],
            "accion": "SECTOR INDUSTRIAL — Ligado a proyectos de infraestructura y minería peruana",
            "icono": "🔧", "color": "#6c7a95", "prioridad": 5
        },
        {
            "id": "R69", "categoria": "Sector",
            "nombre": "TICKER_NYSE",
            "condicion": lambda f, p: f["Ticker"] in ["BAP", "SCCO"],
            "accion": "DOBLE LISTADO — Cotiza en NYSE y BVL, mayor liquidez y visibilidad global",
            "icono": "🗽", "color": "#ffd700", "prioridad": 4
        },
        {
            "id": "R70", "categoria": "Sector",
            "nombre": "TICKER_BVL_LOCAL",
            "condicion": lambda f, p: f["Ticker"].endswith(".LM"),
            "accion": "BOLSA LOCAL — Ticker exclusivo BVL, liquidez menor que NYSE",
            "icono": "🇵🇪", "color": "#6c7a95", "prioridad": 5
        },

        # CATEGORÍA 8: REGLAS COMBINADAS (R71-R80)
        {
            "id": "R71", "categoria": "Combinada",
            "nombre": "COMBINADA_IDEAL_TOTAL",
            "condicion": lambda f, p: f["Crecimiento_%"] >= 2.0 and f["Precio"] >= 5.0 and f["Sector"] == "BVL Real-Time",
            "accion": "SEÑAL IDEAL — Crecimiento positivo + precio saludable + dato en tiempo real",
            "icono": "⭐", "color": "#ffd700", "prioridad": 1
        },
        {
            "id": "R72", "categoria": "Combinada",
            "nombre": "COMBINADA_PEOR_CASO",
            "condicion": lambda f, p: f["Crecimiento_%"] <= -3.0 and f["Precio"] < 2.0,
            "accion": "PEOR CASO — Caída fuerte en activo de bajo precio, salir inmediatamente",
            "icono": "💀", "color": "#ff4757", "prioridad": 1
        },
        {
            "id": "R73", "categoria": "Combinada",
            "nombre": "COMBINADA_CONSERVADOR_IDEAL",
            "condicion": lambda f, p: p == "Conservador" and f["Crecimiento_%"] >= 0.5 and f["Precio"] >= 5.0 and f["Sector"] == "BVL Real-Time",
            "accion": "PORTAFOLIO CONSERVADOR IDEAL — Todos los indicadores alineados",
            "icono": "🏆", "color": "#00e5a0", "prioridad": 1
        },
        {
            "id": "R74", "categoria": "Combinada",
            "nombre": "COMBINADA_AGRESIVO_IDEAL",
            "condicion": lambda f, p: p == "Agresivo" and f["Crecimiento_%"] >= 4.0 and f["Ticker"] in ["BAP","SCCO"],
            "accion": "OPORTUNIDAD AGRESIVA PREMIUM — NYSE + alto crecimiento = señal excepcional",
            "icono": "🎯", "color": "#00e5a0", "prioridad": 1
        },
        {
            "id": "R75", "categoria": "Combinada",
            "nombre": "COMBINADA_BANCO_CRECIMIENTO",
            "condicion": lambda f, p: any(b in f["Empresa"] for b in ["BBVA","BCP","Credicorp"]) and f["Crecimiento_%"] >= 1.0,
            "accion": "BANCO EN ALZA — Sector financiero creciendo, señal macroeconómica positiva",
            "icono": "📈", "color": "#00e5a0", "prioridad": 2
        },
        {
            "id": "R76", "categoria": "Combinada",
            "nombre": "COMBINADA_MINERIA_PREMIUM_ALZA",
            "condicion": lambda f, p: "Southern" in f["Empresa"] and f["Crecimiento_%"] >= 1.0 and f["Precio"] >= 80.0,
            "accion": "MINERÍA PREMIUM ALCISTA — Southern Copper fuerte, señal global de cobre",
            "icono": "🥇", "color": "#ffd700", "prioridad": 2
        },
        {
            "id": "R77", "categoria": "Combinada",
            "nombre": "COMBINADA_CONSUMO_ESTABLE",
            "condicion": lambda f, p: "Alicorp" in f["Empresa"] and abs(f["Crecimiento_%"]) <= 1.5,
            "accion": "CONSUMO DEFENSIVO — Alicorp estable, activo refugio en incertidumbre",
            "icono": "🛡️", "color": "#4ecdc4", "prioridad": 3
        },
        {
            "id": "R78", "categoria": "Combinada",
            "nombre": "COMBINADA_SEÑAL_MIXTA",
            "condicion": lambda f, p: f["Crecimiento_%"] >= 1.0 and f["Sector"] in ("Demo","Demo BVL"),
            "accion": "SEÑAL POSITIVA CON DATO DEMO — Confirmar con fuente oficial antes de operar",
            "icono": "🔍", "color": "#ff6b35", "prioridad": 3
        },
        {
            "id": "R79", "categoria": "Combinada",
            "nombre": "COMBINADA_PORTAFOLIO_BALANCEADO",
            "condicion": lambda f, p: p == "Moderado" and f["Sector"] == "BVL Real-Time" and 0 <= f["Crecimiento_%"] <= 2.0,
            "accion": "PORTAFOLIO BALANCEADO — Condiciones ideales para portafolio moderado diversificado",
            "icono": "⚖️", "color": "#4ecdc4", "prioridad": 2
        },
        {
            "id": "R80", "categoria": "Combinada",
            "nombre": "COMBINADA_ALTO_VALOR_BAJO_RIESGO",
            "condicion": lambda f, p: f["Precio"] >= 50.0 and f["Crecimiento_%"] >= 0 and f["Sector"] == "BVL Real-Time",
            "accion": "VALOR CON SEGURIDAD — Precio alto + crecimiento positivo + dato real = calidad",
            "icono": "💼", "color": "#00e5a0", "prioridad": 2
        },

        # CATEGORÍA 9: ALERTAS Y ADVERTENCIAS (R81-R90)
        {
            "id": "R81", "categoria": "Alerta",
            "nombre": "ALERTA_VOLATILIDAD_EXTREMA",
            "condicion": lambda f, p: abs(f["Crecimiento_%"]) >= 7.0,
            "accion": "⚠️ VOLATILIDAD EXTREMA — Movimiento anormal, verificar noticias corporativas urgente",
            "icono": "🌪️", "color": "#ff4757", "prioridad": 1
        },
        {
            "id": "R82", "categoria": "Alerta",
            "nombre": "ALERTA_PRECIO_CRITICO",
            "condicion": lambda f, p: f["Precio"] < 0.5,
            "accion": "PRECIO CRÍTICO — Posible desvalorización severa o problema estructural",
            "icono": "🚨", "color": "#ff4757", "prioridad": 1
        },
        {
            "id": "R83", "categoria": "Alerta",
            "nombre": "ALERTA_DATO_NO_CONFIABLE",
            "condicion": lambda f, p: f["Sector"] == "Offline",
            "accion": "DATO NO CONFIABLE — Sin conexión a yfinance, no operar con estos datos",
            "icono": "🔴", "color": "#ff4757", "prioridad": 2
        },
        {
            "id": "R84", "categoria": "Alerta",
            "nombre": "ALERTA_LIQUIDEZ_BVL",
            "condicion": lambda f, p: f["Ticker"].endswith(".LM") and f["Crecimiento_%"] >= 5.0,
            "accion": "ALERTA LIQUIDEZ — Alto crecimiento en BVL local, verificar volumen de operaciones",
            "icono": "💧", "color": "#ff6b35", "prioridad": 2
        },
        {
            "id": "R85", "categoria": "Alerta",
            "nombre": "ALERTA_PERFIL_INCOMPATIBLE",
            "condicion": lambda f, p: p == "Conservador" and abs(f["Crecimiento_%"]) >= 4.0,
            "accion": "INCOMPATIBILIDAD DE PERFIL — Este activo no es compatible con perfil conservador",
            "icono": "🚫", "color": "#ff4757", "prioridad": 2
        },
        {
            "id": "R86", "categoria": "Alerta",
            "nombre": "ALERTA_REVERSAL_POTENCIAL",
            "condicion": lambda f, p: f["Crecimiento_%"] <= -4.0 and f["Precio"] >= 20.0,
            "accion": "POSIBLE REVERSAL — Activo sólido en caída fuerte, monitorear para rebote",
            "icono": "🔄", "color": "#3b82f6", "prioridad": 2
        },
        {
            "id": "R87", "categoria": "Alerta",
            "nombre": "ALERTA_CONCENTRACION_RIESGO",
            "condicion": lambda f, p: f["Crecimiento_%"] >= 6.0 and p in ("Moderado","Conservador"),
            "accion": "RIESGO CONCENTRACIÓN — No destinar más del 20% del portafolio a este activo",
            "icono": "📊", "color": "#ff6b35", "prioridad": 2
        },
        {
            "id": "R88", "categoria": "Alerta",
            "nombre": "ALERTA_MACROECONOMICA_PERU",
            "condicion": lambda f, p: f["Ticker"].endswith(".LM") and f["Crecimiento_%"] <= -3.0,
            "accion": "SEÑAL MACRO — Caída en BVL local puede reflejar riesgo político o económico peruano",
            "icono": "🇵🇪", "color": "#ff6b35", "prioridad": 2
        },
        {
            "id": "R89", "categoria": "Alerta",
            "nombre": "ALERTA_TIPO_CAMBIO",
            "condicion": lambda f, p: f["Ticker"] in ["BAP","SCCO"] and f["Crecimiento_%"] <= -2.0,
            "accion": "RIESGO CAMBIARIO — Caída en NYSE puede afectar por tipo de cambio USD/PEN",
            "icono": "💱", "color": "#ff6b35", "prioridad": 3
        },
        {
            "id": "R90", "categoria": "Alerta",
            "nombre": "ALERTA_REVISION_PERIODICA",
            "condicion": lambda f, p: f["Sector"] == "BVL Real-Time" and abs(f["Crecimiento_%"]) <= 0.3,
            "accion": "REVISIÓN PERIÓDICA — Activo en lateralización, revisar cada 5 días",
            "icono": "🔔", "color": "#6c7a95", "prioridad": 5
        },
    ]

    def __init__(self):
        # Índice por categoría, construido una vez, para no recorrer las 90
        # reglas cada vez que alguien pide reglas_por_categoria().
        self._indice_categorias: dict[str, list[dict]] = {}
        for regla in self.REGLAS:
            self._indice_categorias.setdefault(regla["categoria"], []).append(regla)

        self._indice_ids: dict[str, dict] = {r["id"]: r for r in self.REGLAS}

    def evaluar(self, df, perfil: str) -> list:
        """
        Evalúa todas las reglas sobre el DataFrame.
        Retorna lista de hechos activados ordenados por prioridad.
        """
        hechos_activados = []

        for _, fila in df.iterrows():
            reglas_empresa = []

            for regla in self.REGLAS:
                try:
                    if regla["condicion"](fila, perfil):
                        reglas_empresa.append({
                            "empresa":  fila["Empresa"],
                            "ticker":   fila["Ticker"],
                            "regla":    f"[{regla['id']}] {regla['nombre']}",
                            "accion":   regla["accion"],
                            "icono":    regla["icono"],
                            "color":    regla["color"],
                            "prioridad": regla.get("prioridad", 5),
                            "categoria": regla.get("categoria", "General"),
                        })
                except Exception as e:
                    # Antes: "except Exception: continue" — silenciaba todo.
                    # Ahora al menos queda registro de qué regla falló y por qué,
                    # útil para detectar reglas mal formadas o columnas faltantes.
                    logger.warning("Regla %s falló al evaluar %s: %s", regla.get("id"), fila.get("Ticker"), e)
                    continue

            reglas_empresa.sort(key=lambda x: x["prioridad"])
            hechos_activados.extend(reglas_empresa[:3])

        empresas_con_regla = {h["empresa"] for h in hechos_activados}
        for _, fila in df.iterrows():
            if fila["Empresa"] not in empresas_con_regla:
                hechos_activados.append({
                    "empresa":   fila["Empresa"],
                    "ticker":    fila["Ticker"],
                    "regla":     "[R00] SIN_SEÑAL_CLARA",
                    "accion":    "OBSERVAR — No se detectó señal definida. Monitorear.",
                    "icono":     "👁️",
                    "color":     "#6c7a95",
                    "prioridad": 5,
                    "categoria": "General",
                })

        return hechos_activados

    def get_regla_por_id(self, regla_id: str) -> dict | None:
        """Devuelve la definición completa de una regla por su ID (p. ej. 'R42').
        Útil para debugging o para mostrar el catálogo completo en el frontend."""
        return self._indice_ids.get(regla_id)

    def reglas_por_categoria(self, categoria: str) -> list[dict]:
        """Devuelve todas las reglas de una categoría (p. ej. 'Agresivo')."""
        return self._indice_categorias.get(categoria, [])

    def listar_categorias(self) -> list[str]:
        """Devuelve las categorías disponibles, en el orden en que aparecen."""
        return list(self._indice_categorias.keys())

    def exportar_lisp(self, df, perfil: str, ruta: str = None):
        """Exporta hechos evaluados al formato CLIPS .lisp"""
        import os
        if ruta is None:
            base = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', 'data')
            )
            os.makedirs(base, exist_ok=True)
            ruta = os.path.join(base, 'reglas_evaluadas.lisp')

        hechos = self.evaluar(df, perfil)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(f"; Reglas evaluadas — Perfil: {perfil}\n")
            f.write(f"; Total reglas activadas: {len(hechos)}\n")
            f.write(f"; Motor: ClipsRulesEngine v2.0 — 90 reglas\n\n")
            f.write("(setq hechos-reglas '(\n")
            for h in hechos:
                f.write(
                    f'  ("{h["empresa"]}" "{h["ticker"]}" '
                    f'"{h["regla"]}" "{h["accion"]}" "{h["categoria"]}")\n'
                )
            f.write("))\n")
        logger.info("Reglas exportadas: %s", ruta)
        return ruta

    def resumen_por_categoria(self, df, perfil: str) -> dict:
        """Devuelve conteo de reglas activadas por categoría."""
        hechos = self.evaluar(df, perfil)
        resumen = {}
        for h in hechos:
            cat = h.get("categoria", "General")
            resumen[cat] = resumen.get(cat, 0) + 1
        return resumen