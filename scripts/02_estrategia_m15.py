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
df['EMA_20'] = ta.ema(df['Close'], length=20) # EMA 20
df['EMA_200'] = ta.ema(df['Close'], length=200) # EMA 200
adx_df = ta.adx(df['High'], df['Low'], df['Close'], length=14)
df['ADX_14'] = adx_df['ADX_14']    # Extracción del ADX 14
df['DI_Plus'] = adx_df['DMP_14']   # Extracción del +DI
df['DI_Minus'] = adx_df['DMN_14']  # Extracción del -DI
df['ATR_14'] = ta.atr(df['High'], df['Low'], df['Close'], length=14) # Extracción del ATR 14

# 3. LÓGICA BULLISH (Generación de Señales de Compra)
tendencia_fuerte = df['ADX_14'] > 25
toque_actual = (df['Low'] <= df['EMA_20']) & (df['Close'] > df['EMA_20'])
toque_anterior = (df['Low'].shift(1) <= df['EMA_20'].shift(1)) & (df['Close'].shift(1) > df['EMA_20'].shift(1))
pullback_ema = (toque_actual | toque_anterior)
vela_actual_alcista = df['Close'] > df['Open']
vela_ant_bajista = df['Close'].shift(1) < df['Open'].shift(1)
envuelve_cuerpo = vela_actual_alcista & (df['Close'] > df['High'].shift(1))
precio_sobre_ema200 = df['Close'] > df['EMA_200']
di_alcista = df['DI_Plus'] > df['DI_Minus']

# 3.1 FILTRO DE HORARIO: Solo consideramos las señales generadas entre las 9:59 y las 15:01 HORARIO NYSE (EST)
hora_inicio = pd.to_datetime("09:59").time()
hora_fin = pd.to_datetime("15:01").time()
en_horario = (df.index.time >= hora_inicio) & (df.index.time <= hora_fin)
dia_habil = df.index.dayofweek <= 4  # 0 es Lunes, 4 es Viernes
sesion_activa = en_horario & dia_habil

# 4. GENERACIÓN DE SEÑALES
# Incorporamos las nuevas máscaras con el operador & (AND)
df['Senal_Compra'] = tendencia_fuerte & pullback_ema & vela_ant_bajista & envuelve_cuerpo & precio_sobre_ema200 & di_alcista & sesion_activa
df = df.dropna()

# 4.1 Cálculo de los niveles de entrada, stop loss y take profit para las señales de compra
spread = 2.0
multiplicador_sl = 1.5
ratio_tp = 1.2

# 4.1.2 Precio de Entrada Real (Cierre + Spread del Ask)
df.loc[df['Senal_Compra'], 'Precio_Entrada'] = df['Close'] + spread

# 4.1.3 Distancia de Riesgo basada en la volatilidad de ese instante
df.loc[df['Senal_Compra'], 'Riesgo_Puntos'] = df['ATR_14'] * multiplicador_sl

# 4.1.4 Nivel de Stop Loss exacto
df.loc[df['Senal_Compra'], 'SL'] = df['Precio_Entrada'] - df['Riesgo_Puntos']

# 4.1.5 Nivel de Take Profit exacto (Riesgo * 1.2)
df.loc[df['Senal_Compra'], 'TP'] = df['Precio_Entrada'] + (df['Riesgo_Puntos'] * ratio_tp)

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