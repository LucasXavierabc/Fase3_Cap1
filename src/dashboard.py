import streamlit as st
import pandas as pd
import plotly.express as px

# Exibir diretório atual no console
# Configuração da página
st.set_page_config(page_title="Dashboard Agrícola", layout="wide")

# Carregar dados
@st.cache_data
def load_data():
    return pd.read_csv("data.csv")

df = load_data()

# Criar cópia filtrada (atualmente não filtrando nada, pois não há coluna 'label')
df_filtered = df.copy()

# Criar coluna binária para bomba ligada/desligada
df_filtered["bomba_status_bin"] = df_filtered["BOMBA LIGADA/DESLIGADA"].map({"LIGADA": 1, "DESLIGADA": 0})

# Título
st.title("Dashboard de Monitoramento Agrícola")

# Métricas principais
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric(label="Temperatura", value=f"{df_filtered['Temperature'].mean():.1f}°C")
with col2:
    st.metric(label="Umidade", value=f"{df_filtered['Humidity'].mean():.1f}%")
with col3:
    st.metric(label="pH", value=f"{df_filtered['pH'].mean():.2f}")
with col4:
    fosforo_presente = "SIM" if df_filtered['FosforoPresente'].sum() > 0 else "NÃO"
    st.metric(label="Fósforo presente", value=f"{fosforo_presente}")
with col5:
    potassio_presente = "SIM" if df_filtered['PotassioPresente'].sum() > 0 else "NÃO"
    st.metric(label="Potássio presente", value=f"{potassio_presente}")
with col6:
    bomba_ligada = (df_filtered['BOMBA LIGADA/DESLIGADA'] == "LIGADA").sum()
    bomba_desligada = (df_filtered['BOMBA LIGADA/DESLIGADA'] == "DESLIGADA").sum()
    st.metric(label="Bomba Ligada", value=f"{bomba_ligada}")
    st.metric(label="Bomba Desligada", value=f"{bomba_desligada}")

st.markdown("---")

# Colunas para gráficos
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Correlação entre Variáveis")
    corr_cols = ["Humidity", "Temperature", "pH", "FosforoPresente", "PotassioPresente", "bomba_status_bin"]
    corr_matrix = df_filtered[corr_cols].corr()

    fig_corr = px.imshow(
        corr_matrix,
        labels=dict(x="Variáveis", y="Variáveis", color="Correlação"),
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        title="Matriz de Correlação"
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    st.subheader("Distribuição de pH vs Umidade")
    fig_hist = px.histogram(
        df_filtered,
        x="pH",
        y="Humidity",
        color="BOMBA LIGADA/DESLIGADA",
        marginal="box",
        nbins=30,
        title="Distribuição de pH e Umidade por Estado da Bomba"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col_right:
    st.subheader("Dispersão das Variáveis (colorido por Bomba)")
    fig_scatter = px.scatter_matrix(
        df_filtered,
        dimensions=["Humidity", "Temperature", "pH"],
        color="BOMBA LIGADA/DESLIGADA",
        title="Relações entre Variáveis"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Variação Temporal Simulada")
    df_time = df_filtered.reset_index().rename(columns={"index": "Dia"})
    fig_time = px.line(
        df_time,
        x="Dia",
        y=["Temperature", "Humidity"],
        color="BOMBA LIGADA/DESLIGADA",
        labels={"value": "Valor"},
        title="Variação de Temperatura e Umidade com Estado da Bomba"
    )
    st.plotly_chart(fig_time, use_container_width=True)

st.markdown("---")

# Exibição dos dados
st.subheader("Dados Brutos")
st.dataframe(df_filtered, use_container_width=True)