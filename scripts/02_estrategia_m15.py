import pandas as pd
import pandas_ta as ta
import os
import graficador as gr

# --- CONSTRUCCIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ARCHIVO_DATOS = os.path.join(DATA_DIR, "NDX_m15_raw.csv") # Esto se puede ajustar para otros archivos y no solo este csv
ARCHIVO_RESULTADOS = os.path.join(DATA_DIR, "backtest_NDX_m15.csv")

# 1. CARGA DE DATOS LOCALES
print("Cargando Datos")
if not os.path.exists(ARCHIVO_DATOS):
    print("ERROR: No se encontró el archivo de datos. Ejecuta 01_descargar_datos.py primero.")
    exit()

# Es vital indicarle a Pandas que la columna 0 es la fecha y debe parsearla
df = pd.read_csv(ARCHIVO_DATOS, index_col=0, parse_dates=True)

# 2. INDICADORES TÉCNICOS
df['EMA_20'] = ta.ema(df['Close'], length=20)
df['EMA_200'] = ta.ema(df['Close'], length=200)  # Nuevo Indicador: Filtro de Precio Macro

adx_df = ta.adx(df['High'], df['Low'], df['Close'], length=14)
df['ADX_14'] = adx_df['ADX_14']
df['DI_Plus'] = adx_df['DMP_14']   # Extracción del +DI
df['DI_Minus'] = adx_df['DMN_14']  # Extracción del -DI

# 3. LÓGICA BULLISH (MÁSCARAS BOOLEANAS)
tendencia_fuerte = df['ADX_14'] > 25
pullback_ema = (df['Low'] <= df['EMA_20']) & (df['Close'] > df['EMA_20'])
vela_ant_bajista = df['Close'].shift(1) < df['Open'].shift(1)
envuelve_cuerpo = (df['Open'] <= df['Close'].shift(1)) & (df['Close'] > df['Open'].shift(1))

# NUEVOS FILTROS: Dirección Alcista Estricta
precio_sobre_ema200 = df['Close'] > df['EMA_200']
di_alcista = df['DI_Plus'] > df['DI_Minus']

# 4. GENERACIÓN DE SEÑALES
# Incorporamos las nuevas máscaras con el operador & (AND)
df['Senal_Compra'] = tendencia_fuerte & pullback_ema & vela_ant_bajista & envuelve_cuerpo & precio_sobre_ema200 & di_alcista
df = df.dropna()

# 5. GUARDADO Y MÉTRICAS
df.to_csv(ARCHIVO_RESULTADOS)
print("-" * 30)
print(f"Velas procesadas: {len(df)}")
print(f"Señales de compra: {df['Senal_Compra'].sum()}")

if len(df) > 0:
    print(f"Porcentaje de señales de compra: {df['Senal_Compra'].sum() / len(df) * 100:.2f}%")

# 6. GRÁFICO VISUAL
print("Generando gráfico...")
gr.graficar_compras_pulso(df)