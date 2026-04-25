import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="🚚")

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id_nota TEXT PRIMARY KEY,
            vendedor TEXT,
            endereco TEXT,
            status TEXT DEFAULT 'PENDENTE',
            ultima_atualizacao DATETIME
        )
    ''')
    conn.commit()
    return conn

conn = init_db()

# --- CSS PARA CORRIGIR A VISIBILIDADE (AUTO-CONTRASTE) ---
st.markdown("""
    <style>
    /* Forçar cores nítidas e fundo sólido */
    .stApp { background-color: #E5E7EB !important; }
    
    /* Títulos e Textos Principais sempre pretos */
    h1, h2, h3, p, span, label { 
        color: #111827 !important; 
        font-weight: 600 !important; 
    }

    /* Card de Pedido - Super Visível */
    .pedido-card {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 8px;
        border: 2px solid #D1D5DB;
        border-left: 10px solid #059669 !important; /* Verde Forte */
        margin-bottom: 15px;
    }

    /* Card de Alerta/Urgência - Super Contraste */
    .pedido-alerta {
        border-left: 10px solid #DC2626 !important; /* Vermelho Vivo */
        background-color: #FEE2E2 !important;
    }

    /* Ajuste da Barra Lateral para não sumir */
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
    }
    section[data-testid="stSidebar"] * { color: white !important; }

    /* Tags de Vendedor */
    .vendedor-tag {
        background-color: #DBEAFE;
        color: #1E40AF !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 14px;
        display: inline-block;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABEÇALHO ---
st.title("🚚 Painel de Expedição: Controle de Notas")
st.markdown("---")

# Carregar Dados
df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY ultima_atualizacao DESC", conn)

# Colunas Principais
col_mesa, col_patio = st.columns([1.5, 1])

with col_mesa:
    st.subheader("📥 NA MESA (Aguardando)")
    pendentes = df[df['status'] == 'PENDENTE']
    
    if pendentes.empty:
        st.success("Tudo em dia! Nenhuma nota pendente.")
    else:
        for _, row in pendentes.iterrows():
            # Lógica de Alerta Visual
            is_alerta = any(palavra in row['endereco'].lower() for palavra in ['mudar', 'urgente', 'atenção', 'trocar'])
            estilo = "pedido-alerta" if is_alerta else ""
            
            with st.container():
                st.markdown(f"""
                    <div class="pedido-card {estilo}">
                        <div class="vendedor-tag">Vendedor: {row['vendedor']}</div>
                        <h3>Nota: {row['id_nota']}</h3>
                        <p><strong>INFORMAÇÃO:</strong> {row['endereco']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Mandar p/ Carga: {row['id_nota']}", key=row['id_nota'], use_container_width=True):
                    conn.cursor().execute("UPDATE pedidos SET status = 'CONCLUIDO', ultima_atualizacao = ? WHERE id_nota = ?", (datetime.now(), row['id_nota']))
                    conn.commit()
                    st.rerun()

with col_patio:
    st.subheader("✅ NO PÁTIO (Carregado)")
    concluidos = df[df['status'] == 'CONCLUIDO']
    if concluidos.empty:
        st.write("Ainda não houve saídas hoje.")
    else:
        # Tabela com as últimas saídas
        st.table(concluidos[['id_nota', 'vendedor']].head(10))

# BARRA LATERAL (Entrada de Dados)
with st.sidebar:
    st.header("Lançar Nova Nota")
    with st.form("add_nota", clear_on_submit=True):
        n = st.text_input("Número da Nota")
        v = st.text_input("Vendedor")
        e = st.text_area("Observações (Endereço, etc)")
        if st.form_submit_button("CADASTRAR NO SISTEMA"):
            if n and v:
                try:
                    conn.cursor().execute("INSERT INTO pedidos (id_nota, vendedor, endereco, ultima_atualizacao) VALUES (?,?,?,?)", (n,v,e,datetime.now()))
                    conn.commit()
                    st.rerun()
                except:
                    st.error("Nota já cadastrada!")
