"""infrastructure/market/exceptions.py — Errores propios de la capa de mercado."""


class MarketDataError(Exception):
    """No se pudo obtener el dato de mercado ni por Yahoo ni por respaldo."""


class TickerDesconocidoError(MarketDataError):
    """El ticker pedido no está en la lista de activos soportados."""