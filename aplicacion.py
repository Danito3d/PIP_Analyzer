import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from textblob import TextBlob

# Configuración de la página
st.set_page_config(
    page_title="Análisis Forex PIP + Sentiment",
    layout="wide",
    page_icon="📊"
)

# Título y descripción
st.title("🚦 Sistema de Trading Integrado: PIP + Sentiment Analysis")
st.markdown("""
Combina **análisis técnico** (soporte/resistencia) con **sentimiento de mercado** para generar señales.
""")

# --- Sidebar (Controles de usuario) ---
with st.sidebar:
    st.header("⚙️ Parámetros")
    par = st.selectbox("Par Forex", ["EUR/USD", "GBP/USD", "USD/JPY"])
    velas = st.slider("Número de velas", 50, 500, 200)
    rango_pips = st.slider("Rango mínimo de PIPs para ruptura", 10, 50, 20)
    st.markdown("---")
    st.caption("🔍 Datos simulados con fines demostrativos")

# --- 1. Generar datos sintéticos ---
@st.cache_data
def generar_datos(velas):
    np.random.seed(42)
    closes = 1.1000 + np.cumsum(np.random.normal(0.0001, 0.0005, velas))
    df = pd.DataFrame({'close': closes})
    df['high'] = df['close'] + np.random.uniform(0.0002, 0.0004, velas)
    df['low'] = df['close'] - np.random.uniform(0.0002, 0.0004, velas)
    df['soporte'] = df['low'].rolling(50).min()
    df['resistencia'] = df['high'].rolling(50).max()
    return df

df = generar_datos(velas)

# --- 2. Análisis de Sentimiento (simulado) ---
with st.expander("📰 Análisis de Sentimiento en Noticias"):
    noticias = st.text_area("Pega titulares de noticias (uno por línea)", 
                          "La Fed sube tasas\nEl euro se fortalece\nInflación en máximos")
    titulares = [line for line in noticias.split("\n") if line.strip()]
    
    if titulares:
        polaridades = [TextBlob(t).sentiment.polarity for t in titulares]
        sentimiento_promedio = np.mean(polaridades)
        st.metric("Sentimiento Promedio", f"{sentimiento_promedio:.2f}", 
                delta="Alcista" if sentimiento_promedio > 0 else "Bajista")

# --- 3. Señal de Trading ---
ultimo_precio = df['close'].iloc[-1]
resistencia = df['resistencia'].iloc[-1]
soporte = df['soporte'].iloc[-1]
ruptura_compra = (ultimo_precio > resistencia) and ((ultimo_precio - resistencia) * 10000 >= rango_pips)
ruptura_venta = (ultimo_precio < soporte) and ((soporte - ultimo_precio) * 10000 >= rango_pips)

# --- 4. Visualización con Plotly ---
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['close'], name='Precio', line=dict(color='royalblue')))
fig.add_hline(y=resistencia, line_dash="dash", line_color="red", name="Resistencia")
fig.add_hline(y=soporte, line_dash="dash", line_color="green", name="Soporte")

if ruptura_compra:
    fig.add_annotation(x=df.index[-1], y=ultimo_precio, text="🟢 SEÑAL COMPRA", showarrow=True, arrowhead=1)
elif ruptura_venta:
    fig.add_annotation(x=df.index[-1], y=ultimo_precio, text="🔴 SEÑAL VENTA", showarrow=True, arrowhead=1)

fig.update_layout(
    title=f"Análisis de {par} - Últimas {velas} velas",
    xaxis_title="Velas",
    yaxis_title="Precio",
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)

# --- 5. Panel de Resultados ---
col1, col2, col3 = st.columns(3)
col1.metric("Precio Actual", f"{ultimo_precio:.5f}")
col2.metric("Resistencia", f"{resistencia:.5f}", delta=f"{(ultimo_precio - resistencia)*10000:.0f} pips")
col3.metric("Soporte", f"{soporte:.5f}", delta=f"{(soporte - ultimo_precio)*10000:.0f} pips")

if ruptura_compra:
    st.success(f"**SEÑAL DE COMPRA**: Precio rompió resistencia con {rango_pips}+ pips")
elif ruptura_venta:
    st.error(f"**SEÑAL DE VENTA**: Precio rompió soporte con {rango_pips}+ pips")
else:
    st.info("Esperando ruptura significativa...")

# --- 6. Instrucciones ---
with st.expander("ℹ️ Cómo usar esta app"):
    st.markdown("""
    1. **Selecciona un par forex** y ajusta el número de velas.
    2. **Pega titulares de noticias** para análisis de sentimiento.
    3. **Configura el rango mínimo de PIPs** para filtrar rupturas.
    4. Las señales aparecerán automáticamente en el gráfico.
    """)