# src/tools/finance.py
import yfinance as yf
from langchain_core.tools import tool

@tool
def obtener_precio_accion(ticker: str) -> str:
    """
    Obtiene el precio actual y la moneda de una acción en la bolsa de valores.
    El usuario debe proporcionar el símbolo bursátil (ticker).
    Ejemplos de tickers: 'AAPL' para Apple, 'AMZN' para Amazon, 'SAN.MC' para Banco Santander.
    """
    try:
        accion = yf.Ticker(ticker)
        precio = accion.info.get('currentPrice', 'No disponible')
        moneda = accion.info.get('financialCurrency', 'USD')
        
        if precio == 'No disponible':
            return f"No se ha encontrado el precio para el ticker: {ticker}."
            
        return f"DATO EN TIEMPO REAL: El precio actual de {ticker} es de {precio} {moneda}."
    except Exception as e:
        return f"Error en la API financiera al buscar {ticker}. Detalle: {str(e)}"