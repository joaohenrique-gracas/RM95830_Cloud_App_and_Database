import streamlit as st
import requests
import pandas as pd

# Configurações iniciais da página
st.set_page_config(page_title="Dashboard Climático", page_icon="🌤️")

# Substitua pela sua chave da OpenWeatherMap
API_KEY = "014705e362b53e6504a77422d23e2aae"

def buscar_clima(cidade):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={API_KEY}&units=metric&lang=pt_br"
    response = requests.get(url)
    return response.json()

# --- Interface do Usuário ---
st.title("🌡️ Weather Dashboard")
cidade = st.text_input("Digite o nome da cidade:", "São Paulo")

if st.button("Verificar Clima"):
    dados = buscar_clima(cidade)
    
    if dados.get("cod") == 200:
        # Extração de dados
        temp = dados["main"]["temp"]
        umidade = dados["main"]["humidity"]
        vento = dados["wind"]["speed"]
        descricao = dados["weather"][0]["description"].capitalize()
        icone = dados["weather"][0]["icon"]

        # Layout em colunas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Temperatura", f"{temp}°C")
        with col2:
            st.metric("Umidade", f"{umidade}%")
        with col3:
            st.metric("Vento", f"{vento} m/s")

        st.subheader(f"Condição atual em {cidade}: {descricao}")

    else:
        st.error("Cidade não encontrada. Verifique o nome e tente novamente.")

st.sidebar.info("Dashboard de clima simples para monitoramento de cidades ao redor do mundo.")