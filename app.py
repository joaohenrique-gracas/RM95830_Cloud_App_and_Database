import streamlit as st
import requests
import pandas as pd
import pyodbc
import os
from dotenv import load_dotenv 

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Dashboard Climático", page_icon="🌤️")

# Configuração do Banco (Ajuste as variáveis de ambiente na sua VM ou preencha aqui)
# Dica: Na VM, você pode rodar 'export DB_SERVER=seu_servidor.database.windows.net'
server = "sqldb-server-rm95830.database.windows.net"
database = "database-inova"
username = "sqldb-rm95839-adm"
password = "fiap-rm95830-app-db"

# String de conexão seguindo o modelo do professor
conn_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
)

# Chave da API OpenWeatherMap
API_KEY = "014705e362b53e6504a77422d23e2aae"

# --- FUNÇÕES DE DADOS ---

def get_connection():
    return pyodbc.connect(conn_str)

def salvar_historico(cidade, temp, umidade, descricao):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Certifique-se de que a tabela 'clima' exista no seu SQL Azure
        cursor.execute("""
            INSERT INTO clima (cidade, temperatura, umidade, descricao, data_consulta)
            VALUES (?, ?, ?, ?, GETDATE())
        """, (cidade, temp, umidade, descricao))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Erro ao salvar no banco: {e}")

def buscar_clima(cidade):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&units=metric&lang=pt_br"
    response = requests.get(url)
    return response.json()

def listar_historico():
    try:
        conn = get_connection()
        query = "SELECT TOP 10 * FROM clima ORDER BY data_consulta DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# --- INTERFACE DO USUÁRIO ---
st.title("🌡️ Weather Dashboard")
cidade_input = st.text_input("Digite o nome da cidade:", "São Paulo")

if st.button("Verificar Clima"):
    dados = buscar_clima(cidade_input)
    
    if dados.get("cod") == 200:
        # Extração de dados
        temp = dados["main"]["temp"]
        umidade = dados["main"]["humidity"]
        vento = dados["wind"]["speed"]
        descricao = dados["weather"][0]["description"].capitalize()
        
        # Layout em colunas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Temperatura", f"{temp}°C")
        with col2:
            st.metric("Umidade", f"{umidade}%")
        with col3:
            st.metric("Vento", f"{vento} m/s")

        st.subheader(f"Condição atual em {cidade_input}: {descricao}")

        # --- PERSISTÊNCIA NA AZURE ---
        salvar_historico(cidade_input, temp, umidade, descricao)
        st.success("Dados salvos no Azure SQL com sucesso!")

    else:
        st.error("Cidade não encontrada.")

# --- SEÇÃO DE HISTÓRICO (CRUD - READ) ---
st.divider()
st.subheader("📜 Últimas Consultas (Banco de Dados)")
if st.checkbox("Mostrar histórico do banco"):
    df_historico = listar_historico()
    if not df_historico.empty:
        st.dataframe(df_historico, use_container_width=True)
    else:
        st.write("Nenhum dado encontrado no banco.")

st.sidebar.info("Dashboard integrado ao Azure SQL Database.")
