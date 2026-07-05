"""backend/schemas.py — Modelos Pydantic compartidos por los routers."""
from typing import List, Optional
from pydantic import BaseModel


class ActivoResponse(BaseModel):
    empresa:     str
    ticker:      str
    precio:      float
    crecimiento: float
    sector:      str


class ReglaResponse(BaseModel):
    empresa: str
    ticker:  str
    regla:   str
    accion:  str
    icono:   str
    color:   str


class AnalisisRequest(BaseModel):
    tickers: List[str]
    perfil:  str = "Moderado"


class AnalisisResponse(BaseModel):
    activos:     List[ActivoResponse]
    reglas:      List[ReglaResponse]
    analisis_ia: Optional[str] = None


class ChatMessage(BaseModel):
    role:    str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    perfil:  str = "Moderado"