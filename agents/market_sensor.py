"""agents/market_sensor.py — Sensor de mercado (con esteroides).

Mejoras sobre la versión original:
- FETCH EN PARALELO con ThreadPoolExecutor. Antes se consultaba un ticker a
  la vez (secuencial): con 7 tickers y 8s de timeout cada uno, el peor caso
  tardaba ~56s. Ahora todos se consultan a la vez → ~8s en el peor caso.
- CACHE TTL de 30s: si pides los mismos tickers varias veces seguidas
  (dashboard refrescando), no se vuelve a golpear Yahoo Finance.
- Logging en vez de prints/silenciar excepciones con `except:` desnudo.
- `.stats()` para observabilidad (requests, cache hits).

La interfaz pública es IDÉNTICA a la anterior: `.activos`, `percibir_mercado()`,
`exportar_hechos_lisp()`. Nada que ya use MarketSensor necesita cambiar.
"""
from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import pandas as pd
import yfinance as yf

from agents._cache import TTLCache

logger = logging.getLogger(__name__)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)


class MarketSensor:
    def __init__(self, cache_ttl_seconds: float = 30.0, max_workers: int = 7) -> None:
        self.activos = {
            "ALICORC1.LM": "Alicorp",
            "BBVAC1.LM":   "BBVA Perú",
            "CPACASC1.LM": "Cementos Pacasmayo",
            "FERREYC1.LM": "Ferreycorp",
            "VOLCABC1.LM": "Volcan Minera",
            "BAP":         "Credicorp (BCP)",
            "SCCO":        "Southern Copper",
        }
        # Precios de respaldo realistas BVL 2024
        self._respaldo = {
            "ALICORC1.LM": (8.45,   1.20),
            "BBVAC1.LM":   (5.30,  -0.75),
            "CPACASC1.LM": (4.80,   0.42),
            "FERREYC1.LM": (2.95,   2.10),
            "VOLCABC1.LM": (0.48,  -1.50),
            "BAP":         (185.20, 0.85),
            "SCCO":        (98.60,  1.35),
        }
        self._max_workers = max_workers
        self._cache = TTLCache(ttl_seconds=cache_ttl_seconds)
        self.stats = {"requests": 0, "cache_hits": 0}

    def _precio_yfinance(self, ticker: str) -> Optional[tuple[float, float]]:
        try:
            df = yf.download(
                ticker, period="5d", interval="1d",
                progress=False, auto_adjust=True, timeout=8,
            )
            if df is None or df.empty:
                return None
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            col = next((c for c in df.columns if "close" in str(c).lower()), None)
            if col is None:
                return None
            serie = df[col].dropna()
            if len(serie) < 1:
                return None
            actual = float(serie.iloc[-1])
            cambio = 0.0
            if len(serie) >= 2:
                anterior = float(serie.iloc[-2])
                if anterior > 0:
                    cambio = ((actual - anterior) / anterior) * 100
            return round(actual, 2), round(cambio, 2)
        except Exception as exc:
            logger.debug("yfinance falló para %s: %s — se usará respaldo", ticker, exc)
            return None

    def _fila(self, ticker: str) -> dict:
        nombre = self.activos.get(ticker, ticker)
        resultado = self._precio_yfinance(ticker)
        if resultado:
            precio, cambio = resultado
            sector = "BVL Real-Time"
        else:
            precio, cambio = self._respaldo.get(ticker, (10.0, 0.0))
            sector = "Demo"
        return {
            "Empresa": nombre, "Ticker": ticker,
            "Precio": precio, "Crecimiento_%": cambio, "Sector": sector,
        }

    def percibir_mercado(self, lista_tickers: Optional[list[str]] = None) -> pd.DataFrame:
        tickers = lista_tickers or list(self.activos.keys())
        self.stats["requests"] += 1

        cache_key = ",".join(sorted(tickers))
        cacheado = self._cache.get(cache_key)
        if cacheado is not None:
            self.stats["cache_hits"] += 1
            return cacheado.copy()

        datos: list[dict] = []
        with ThreadPoolExecutor(max_workers=min(self._max_workers, len(tickers) or 1)) as executor:
            futuros = {executor.submit(self._fila, t): t for t in tickers}
            for futuro in as_completed(futuros):
                datos.append(futuro.result())

        # as_completed no garantiza el orden — lo reordenamos según lo pedido
        orden = {t: i for i, t in enumerate(tickers)}
        datos.sort(key=lambda d: orden.get(d["Ticker"], 999))

        # GARANTÍA: nunca retorna vacío
        if not datos:
            for ticker in tickers:
                p, c = self._respaldo.get(ticker, (10.0, 0.0))
                datos.append({
                    "Empresa": self.activos.get(ticker, ticker),
                    "Ticker": ticker, "Precio": p,
                    "Crecimiento_%": c, "Sector": "Demo",
                })

        df = pd.DataFrame(datos)
        self._cache.set(cache_key, df)
        return df

    def invalidar_cache(self) -> None:
        """Fuerza a que el próximo request vuelva a consultar Yahoo Finance."""
        self._cache.clear()

    def exportar_hechos_lisp(self, df: pd.DataFrame) -> str:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        ruta_dir = os.path.join(base, "data")
        os.makedirs(ruta_dir, exist_ok=True)
        ruta = os.path.join(ruta_dir, "hechos_mercado.lisp")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("(setq hechos-mercado '(\n")
            for _, fila in df.iterrows():
                f.write(f'  ("{fila["Empresa"]}" {fila["Precio"]} {fila["Crecimiento_%"]} "{fila["Sector"]}")\n')
            f.write("))\n")
        logger.info("Hechos exportados: %s", ruta)
        return ruta


if __name__ == "__main__":
    s = MarketSensor()
    df = s.percibir_mercado()
    print(df[["Empresa", "Precio", "Crecimiento_%", "Sector"]].to_string(index=False))