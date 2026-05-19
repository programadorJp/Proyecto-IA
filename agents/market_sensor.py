import yfinance as yf
import pandas as pd
import logging
import os

logging.getLogger('yfinance').setLevel(logging.CRITICAL)

class MarketSensor:
    def __init__(self):
        self.activos = {
            'ALICORC1.LM': 'Alicorp',
            'BBVAC1.LM':   'BBVA Perú',
            'CPACASC1.LM': 'Cementos Pacasmayo',
            'FERREYC1.LM': 'Ferreycorp',
            'VOLCABC1.LM': 'Volcan Minera',
            'BAP':         'Credicorp (BCP)',
            'SCCO':        'Southern Copper'
        }
        # Precios de respaldo realistas BVL 2024
        self._respaldo = {
            'ALICORC1.LM': (8.45,   1.20),
            'BBVAC1.LM':   (5.30,  -0.75),
            'CPACASC1.LM': (4.80,   0.42),
            'FERREYC1.LM': (2.95,   2.10),
            'VOLCABC1.LM': (0.48,  -1.50),
            'BAP':         (185.20, 0.85),
            'SCCO':        (98.60,  1.35),
        }

    def _precio_yfinance(self, ticker):
        try:
            df = yf.download(ticker, period="5d", interval="1d",
                             progress=False, auto_adjust=True, timeout=8)
            if df is None or df.empty:
                return None
            # Aplanar MultiIndex si existe
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            col = next((c for c in df.columns if 'close' in str(c).lower()), None)
            if col is None:
                return None
            serie = df[col].dropna()
            if len(serie) < 1:
                return None
            actual = float(serie.iloc[-1])
            cambio = 0.0
            if len(serie) >= 2:
                ant = float(serie.iloc[-2])
                if ant > 0:
                    cambio = ((actual - ant) / ant) * 100
            return round(actual, 2), round(cambio, 2)
        except:
            return None

    def percibir_mercado(self, lista_tickers=None):
        tickers = lista_tickers or list(self.activos.keys())
        datos = []

        for ticker in tickers:
            nombre = self.activos.get(ticker, ticker)
            resultado = self._precio_yfinance(ticker)

            if resultado:
                precio, cambio = resultado
                sector = "BVL Real-Time"
            else:
                precio, cambio = self._respaldo.get(ticker, (10.0, 0.0))
                sector = "Demo"

            datos.append({
                "Empresa":       nombre,
                "Ticker":        ticker,
                "Precio":        precio,
                "Crecimiento_%": cambio,
                "Sector":        sector
            })

        # GARANTÍA: nunca retorna vacío
        if not datos:
            for ticker in tickers:
                p, c = self._respaldo.get(ticker, (10.0, 0.0))
                datos.append({
                    "Empresa": self.activos.get(ticker, ticker),
                    "Ticker": ticker, "Precio": p,
                    "Crecimiento_%": c, "Sector": "Demo"
                })

        return pd.DataFrame(datos)

    def exportar_hechos_lisp(self, df):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        ruta_dir = os.path.join(base, 'data')
        os.makedirs(ruta_dir, exist_ok=True)
        ruta = os.path.join(ruta_dir, 'hechos_mercado.lisp')
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("(setq hechos-mercado '(\n")
            for _, fila in df.iterrows():
                f.write(f'  ("{fila["Empresa"]}" {fila["Precio"]} {fila["Crecimiento_%"]} "{fila["Sector"]}")\n')
            f.write("))\n")
        print(f"Hechos exportados: {ruta}")

if __name__ == "__main__":
    s = MarketSensor()
    df = s.percibir_mercado()
    print(df[['Empresa','Precio','Crecimiento_%','Sector']].to_string(index=False))