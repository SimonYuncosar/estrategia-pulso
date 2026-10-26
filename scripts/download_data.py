import yfinance as yf
import pandas as pd
import os

# --- CONSTRUCCIÓN DE RUTAS ROBUSTAS ---
# 1. Obtiene la ruta de este script (carpeta 'scripts')
# 2. Sube un nivel para llegar a la carpeta principal ('pulso')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
GRAFICOS_DIR = os.path.join(BASE_DIR, "graficos")


def descargar_datos_historicos_yfinance():
    activo = '^NDX'  # Seleccionar el simbolo
    intervalo = '15m'  # Intervalo de tiempo
    periodo = '60d'  # Periodo de tiempo
    print("Conectando con Yahoo Finance para descargar {activo} con intervalo {intervalo} y periodo {periodo}...".format(activo=activo, intervalo=intervalo, periodo=periodo))
    df = yf.download(activo, interval=intervalo, period=periodo)

    # Manejo del MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)

    # Ruta de guardado
    archivo_salida = os.path.join(DATA_DIR, "NDX_m15_raw.csv")
    
    # Exportar. No limpiamos NA aquí, guardamos los datos crudos puros.
    df.to_csv(archivo_salida)
    
    print(f"Éxito: {len(df)} velas descargadas y guardadas en:")
    print(f"-> {archivo_salida}")

if __name__ == "__main__":
    descargar_datos_historicos_yfinance()