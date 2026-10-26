import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import os
import pandas as pd
from datetime import datetime

pio.renderers.default = 'browser'

# --- CONSTRUCCIÓN DE RUTAS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAFICOS_DIR = os.path.join(BASE_DIR, "graficos")

def graficar_compras_pulso(df, titulo="Backtest Estrategia", nombre_archivo=None):
    # Generar la marca de tiempo única para este ejecutable
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Inyección de timestamp: garantiza un nuevo archivo en cada ejecución
    if nombre_archivo is None:
        nombre_archivo = f"grafico_backtest_{timestamp}.html"
    else:
        base, extension = os.path.splitext(nombre_archivo)
        if not extension:
            extension = ".html"
        nombre_archivo = f"{base}_{timestamp}{extension}"

    fechas_ejex = df.index.strftime('%Y-%m-%d %H:%M')
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, row_heights=[0.8, 0.2])

    fig.add_trace(go.Candlestick(
        x=fechas_ejex, open=df['Open'], high=df['High'], 
        low=df['Low'], close=df['Close'], name='Precio'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=fechas_ejex, y=df['EMA_20'], 
        line=dict(color='cyan', width=1.5), name='EMA 20'
    ), row=1, col=1)

    compras = df[df['Senal_Compra'] == True]
    fechas_senales = compras.index.strftime('%Y-%m-%d %H:%M')
    
    fig.add_trace(go.Scatter(
        x=fechas_senales, y=compras['Low'] - 10, mode='markers',
        marker=dict(symbol='triangle-up', color='lime', size=14, line=dict(color='black', width=1)),
        name='Señal Compra'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=fechas_ejex, y=df['ADX_14'], 
        line=dict(color='magenta', width=1.5), name='ADX 14'
    ), row=2, col=1)
    
    fig.add_hline(y=25, line_dash="dash", line_color="red", row=2, col=1, annotation_text="Filtro Tendencia (25)")

    # 1. Separadores de sesión (líneas verticales rojas discontinuas)
    inicios_dias = df.groupby(df.index.date).apply(
        lambda sub_df: sub_df.index[0].strftime('%Y-%m-%d %H:%M')
    )
    for sesion in inicios_dias:
        fig.add_vline(x=sesion, line_dash="dash", line_color="red", opacity=0.6, row=1, col=1)
        fig.add_vline(x=sesion, line_dash="dash", line_color="red", opacity=0.6, row=2, col=1)

    # 2. Eliminación absoluta de huecos forzando el eje a categorías
    fig.update_xaxes(type='category', nticks=15)
    
    fig.update_layout(
        title=titulo, 
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        height=800
    )
    
    # Asegurar que el directorio de salida existe
    os.makedirs(GRAFICOS_DIR, exist_ok=True)
    ruta_html = os.path.join(GRAFICOS_DIR, nombre_archivo)

    # Guardar archivo estático
    fig.write_html(ruta_html)
    print("\n[OK] Gráfico generado con éxito:")
    print(f"     Archivo: {nombre_archivo}")
    print(f"     Ruta:    {ruta_html}\n")
    
    fig.show()