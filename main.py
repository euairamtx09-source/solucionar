import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuração da página para ocupar a tela toda (bom para PC)
st.set_page_config(layout="wide", page_title="ExpedFlow - Painel de Controle")

def carregar_dados():
    conn = sqlite3.connect('expedicao.db')
    df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY ultima_atualizacao DESC", conn)
    conn.close()
    return df

st.title("🚀 ExpedFlow: Gestão de Notas e Logística")

# Barra Lateral com Filtros
st.sidebar.header("Filtros Rápidos")
busca = st.sidebar.text_input("🔍 Buscar Nota ou Cliente")
filtro_alerta = st.sidebar.checkbox("Mostrar apenas ALERTAS CRÍTICOS")

# Carregar os dados do banco
df = carregar_dados()

if busca:
    df = df[df['id_nota'].str.contains(busca) | df['endereco'].str.contains(busca)]

if filtro_alerta:
    df = df[df['alerta_critico'] == 1]

# Layout em Colunas (Kanban)
col1, col2, col3 = st.columns(3)

with col1:
    st.header("📥 Entrada / Triagem")
    notas_pendentes = df[df['status'] == 'PENDENTE']
    for _, nota in notas_pendentes.iterrows():
        cor = "red" if nota['alerta_critico'] == 1 else "white"
        with st.container(border=True):
            if nota['alerta_critico'] == 1:
                st.error(f"⚠️ MUDANÇA: Nota {nota['id_nota']}")
            else:
                st.subheader(f"Nota: {nota['id_nota']}")
            
            st.write(f"**Vendedor:** {nota['vendedor']}")
            st.write(f"**Info/Endereço:** {nota['endereco']}")
            if st.button(f"Faturar {nota['id_nota']}", key=f"fat_{nota['id_nota']}"):
                # Lógica para mudar status no banco aqui
                pass

with col2:
    st.header("⚙️ Em Faturamento")
    # Aqui apareceriam as notas que você está emitindo agora

with col3:
    st.header("🚚 Pronto p/ Carga")
    # Aqui o pessoal do pátio olharia pelo celular
