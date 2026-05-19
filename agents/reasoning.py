"""reasoning.py — Orquestador del Agente Inteligente
Coordina MarketSensor + ClipsRulesEngine + ExpertBrain"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.market_sensor import MarketSensor
from agents.clips_rules import ClipsRulesEngine
from agents.expert_brain import ExpertBrain

def ejecutar_analisis(perfil: str = "Moderado", tickers: list = None):
    """
    Pipeline completo del agente:
    1. Percepción → MarketSensor descarga precios reales
    2. Exportación → genera hechos_mercado.lisp
    3. Reglas CLIPS → evalúa señales según perfil
    4. IA → ExpertBrain genera análisis narrativo
    """
    sensor = MarketSensor()
    clips  = ClipsRulesEngine()
    brain  = ExpertBrain()

    # 1. Percepción
    df = sensor.percibir_mercado(tickers)
    print(f"\n✅ Datos obtenidos: {len(df)} activos")
    print(df[["Empresa", "Precio", "Crecimiento_%", "Sector"]].to_string(index=False))

    # 2. Exportar hechos para CLISP externo
    sensor.exportar_hechos_lisp(df)
    clips.exportar_lisp(df, perfil)

    # 3. Reglas CLIPS
    print(f"\n📋 Reglas activadas — Perfil: {perfil}")
    reglas = clips.evaluar(df, perfil)
    for r in reglas:
        print(f"  {r['icono']}  {r['empresa']:25s} | {r['regla']:35s} → {r['accion']}")

    # 4. Análisis IA
    print("\n🤖 Análisis ExpertBrain (Gemini):")
    analisis = brain.procesar_estrategia(df)
    print(analisis)

    return {
        "df": df,
        "reglas": reglas,
        "analisis_ia": analisis,
    }


if __name__ == "__main__":
    resultado = ejecutar_analisis(perfil="Moderado")
    print("\n✔ Pipeline completado.")