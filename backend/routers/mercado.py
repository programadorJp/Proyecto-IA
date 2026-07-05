"""backend/routers/mercado.py — Datos de mercado y motor de reglas CLIPS."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends

from backend.dependencies import get_sensor, get_clips
from backend.schemas import ActivoResponse, ReglaResponse

router = APIRouter(tags=["Mercado"])


@router.get("/tickers")
def get_tickers(sensor=Depends(get_sensor)):
    return {"tickers": sensor.activos}


@router.get("/activos", response_model=List[ActivoResponse])
def get_activos(
    tickers: Optional[str] = Query(default=None),
    sensor=Depends(get_sensor),
):
    lista = tickers.split(",") if tickers else list(sensor.activos.keys())
    invalidos = [t for t in lista if t not in sensor.activos]
    if invalidos:
        raise HTTPException(400, detail=f"Tickers no reconocidos: {invalidos}")

    df = sensor.percibir_mercado(lista)
    sensor.exportar_hechos_lisp(df)

    return [
        ActivoResponse(
            empresa=row["Empresa"],
            ticker=row["Ticker"],
            precio=row["Precio"],
            crecimiento=row["Crecimiento_%"],
            sector=row["Sector"],
        )
        for _, row in df.iterrows()
    ]


@router.get("/reglas", response_model=List[ReglaResponse], tags=["Motor CLIPS"])
def get_reglas(
    tickers: Optional[str] = Query(default=None),
    perfil: str = Query(default="Moderado"),
    sensor=Depends(get_sensor),
    clips=Depends(get_clips),
):
    if perfil not in ("Conservador", "Moderado", "Agresivo"):
        raise HTTPException(400, detail="Perfil inválido.")

    lista = tickers.split(",") if tickers else list(sensor.activos.keys())
    df = sensor.percibir_mercado(lista)
    reglas = clips.evaluar(df, perfil)
    return [ReglaResponse(**r) for r in reglas]


@router.get("/estado-mercado")
def get_estado_mercado(sensor=Depends(get_sensor)):
    df = sensor.percibir_mercado()
    promedio = df["Crecimiento_%"].mean()
    return {
        "activos_totales": len(df),
        "promedio_crecimiento": round(promedio, 2),
        "al_alza": int(len(df[df["Crecimiento_%"] > 0])),
        "a_la_baja": int(len(df[df["Crecimiento_%"] < 0])),
        "sentimiento_mercado": (
            "Alcista 📈" if promedio > 1
            else "Bajista 📉" if promedio < -1
            else "Neutral ➡️"
        ),
        "activos": [
            {
                "empresa": row["Empresa"],
                "ticker": row["Ticker"],
                "precio": row["Precio"],
                "crecimiento": row["Crecimiento_%"],
            }
            for _, row in df.iterrows()
        ],
    }