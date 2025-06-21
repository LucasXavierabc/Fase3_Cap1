import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import oracledb
from datetime import datetime
import time

# Configuração da página
st.set_page_config(page_title="Dashboard Agrícola", layout="wide")

# Configurações do banco (mesmo do arquivo API)
ORACLE_CONFIG = {
    'dsn': 'oracle.fiap.com.br:1521/orcl',
    'user': 'RM566449',
    'password': '181101'
}

TABELA = 'irrigacao_dados'

# Opção 1: Conectar diretamente ao banco
def conectar_oracle():
    """Conecta ao Oracle com retry"""
    for tentativa in range(3):
        try:
            conn = oracledb.connect(
                user=ORACLE_CONFIG['user'],
                password=ORACLE_CONFIG['password'],
                dsn=ORACLE_CONFIG['dsn']
            )
            return conn
        except Exception as e:
            if tentativa == 2:
                raise e
            time.sleep(1)
    return None

@st.cache_data(ttl=30)  # Cache por 30 segundos
def load_data_from_oracle():
    """Carrega dados diretamente do Oracle"""
    try:
        conn = conectar_oracle()
        
        # Query para buscar os dados
        query = f"""
            SELECT 
                humidity as "Humidity",
                temperature as "Temperature", 
                ph as "pH",
                fosforo_presente as "FosforoPresente",
                potassio_presente as "PotassioPresente",
                bomba_status as "BOMBA LIGADA/DESLIGADA",
                data_coleta
            FROM {TABELA}
            ORDER BY data_coleta DESC
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Converter status da bomba para o formato esperado
        df["BOMBA LIGADA/DESLIGADA"] = df["BOMBA LIGADA/DESLIGADA"].map({
            "LIGADA": "LIGADA",
            "DESLIGADA": "DESLIGADA"
        })
        
        return df
        
    except Exception as e:
        st.error(f"Erro ao conectar ao banco: {e}")
        return pd.DataFrame()  # Retorna DataFrame vazio em caso de erro

# Opção 2: Usar a API (caso a API esteja rodando)
@st.cache_data(ttl=30)
def load_data_from_api(api_url="http://localhost:5000"):
    """Carrega dados através da API"""
    try:
        response = requests.get(f"{api_url}/dados/consulta", timeout=10)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data['dados'])
            
            # Renomear colunas para manter compatibilidade
            column_mapping = {
                'HUMIDITY': 'Humidity',
                'TEMPERATURE': 'Temperature',
                'PH': 'pH',
                'FOSFORO_PRESENTE': 'FosforoPresente',
                'POTASSIO_PRESENTE': 'PotassioPresente',
                'BOMBA_STATUS': 'BOMBA LIGADA/DESLIGADA'
            }
            
            df = df.rename(columns=column_mapping)
            return df
        else:
            st.error(f"Erro na API: {response.status_code}")
            return pd.DataFrame()
            
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com a API: {e}")
        return pd.DataFrame()

# Sidebar para escolher fonte de dados
st.sidebar.title("Configurações")
fonte_dados = st.sidebar.selectbox(
    "Fonte dos dados:",
    ["Banco Oracle Direto", "API (localhost:5000)"]
)

# Botão para atualizar dados
if st.sidebar.button("🔄 Atualizar Dados"):
    st.cache_data.clear()
    st.rerun()

# Carregar dados baseado na escolha
if fonte_dados == "Banco Oracle Direto":
    df = load_data_from_oracle()
else:
    df = load_data_from_api()

# Verificar se há dados
if df.empty:
    st.error("Não foi possível carregar os dados. Verifique a conexão.")
    st.stop()

# Filtrar dados (mantendo a estrutura original)
df_filtered = df.copy()

# Criar coluna binária para bomba ligada/desligada
df_filtered["bomba_status_bin"] = df_filtered["BOMBA LIGADA/DESLIGADA"].map({"LIGADA": 1, "DESLIGADA": 0})

# Título
st.title("Dashboard de Monitoramento Agrícola")

# Informações sobre a fonte de dados
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    st.info(f"📊 Fonte: {fonte_dados}")
with col_info2:
    st.info(f"📈 Total de registros: {len(df_filtered)}")
with col_info3:
    if 'data_coleta' in df_filtered.columns:
        ultima_atualizacao = df_filtered['data_coleta'].max()
        st.info(f"🕒 Última coleta: {ultima_atualizacao}")

# Métricas principais
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    if len(df_filtered) > 0:
        st.metric(label="Temperatura", value=f"{df_filtered['Temperature'].mean():.1f}°C")
    else:
        st.metric(label="Temperatura", value="N/A")

with col2:
    if len(df_filtered) > 0:
        st.metric(label="Umidade", value=f"{df_filtered['Humidity'].mean():.1f}%")
    else:
        st.metric(label="Umidade", value="N/A")

with col3:
    if len(df_filtered) > 0:
        st.metric(label="pH", value=f"{df_filtered['pH'].mean():.2f}")
    else:
        st.metric(label="pH", value="N/A")

with col4:
    if len(df_filtered) > 0:
        fosforo_presente = "SIM" if df_filtered['FosforoPresente'].sum() > 0 else "NÃO"
        st.metric(label="Fósforo presente", value=f"{fosforo_presente}")
    else:
        st.metric(label="Fósforo presente", value="N/A")

with col5:
    if len(df_filtered) > 0:
        potassio_presente = "SIM" if df_filtered['PotassioPresente'].sum() > 0 else "NÃO"
        st.metric(label="Potássio presente", value=f"{potassio_presente}")
    else:
        st.metric(label="Potássio presente", value="N/A")

with col6:
    if len(df_filtered) > 0:
        bomba_ligada = (df_filtered['BOMBA LIGADA/DESLIGADA'] == "LIGADA").sum()
        bomba_desligada = (df_filtered['BOMBA LIGADA/DESLIGADA'] == "DESLIGADA").sum()
        st.metric(label="Bomba Ligada", value=f"{bomba_ligada}")
        st.metric(label="Bomba Desligada", value=f"{bomba_desligada}")
    else:
        st.metric(label="Bomba Ligada", value="N/A")
        st.metric(label="Bomba Desligada", value="N/A")

st.markdown("---")

# Só mostrar gráficos se houver dados
if len(df_filtered) > 0:
    # Colunas para gráficos
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Correlação entre Variáveis")
        corr_cols = ["Humidity", "Temperature", "pH", "FosforoPresente", "PotassioPresente", "bomba_status_bin"]
        # Filtrar apenas colunas que existem
        corr_cols = [col for col in corr_cols if col in df_filtered.columns]
        
        if len(corr_cols) > 1:
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
    
    # Adicionar filtros para os dados
    st.sidebar.markdown("### Filtros dos Dados")
    
    # Filtro por status da bomba
    status_options = df_filtered['BOMBA LIGADA/DESLIGADA'].unique().tolist()
    selected_status = st.sidebar.multiselect(
        "Status da Bomba:",
        options=status_options,
        default=status_options
    )
    
    # Aplicar filtros
    if selected_status:
        df_display = df_filtered[df_filtered['BOMBA LIGADA/DESLIGADA'].isin(selected_status)]
    else:
        df_display = df_filtered
    
    # Mostrar número de registros filtrados
    st.write(f"Mostrando {len(df_display)} de {len(df_filtered)} registros")
    
    st.dataframe(df_display, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado para exibir gráficos.")

# Adicionar seção de status da conexão
st.sidebar.markdown("---")
st.sidebar.markdown("### Status da Conexão")

if fonte_dados == "API (localhost:5000)":
    try:
        health_response = requests.get("http://localhost:5000/health", timeout=5)
        if health_response.status_code == 200:
            st.sidebar.success("✅ API Online")
        else:
            st.sidebar.error("❌ API com problemas")
    except:
        st.sidebar.error("❌ API Offline")
else:
    try:
        conn = conectar_oracle()
        if conn:
            conn.close()
            st.sidebar.success("✅ Banco Oracle Conectado")
        else:
            st.sidebar.error("❌ Erro na conexão Oracle")
    except:
        st.sidebar.error("❌ Banco Oracle Offline")