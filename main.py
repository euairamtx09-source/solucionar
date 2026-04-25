import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64

# --- 1. CONFIGURAÇÃO DE SEGURANÇA E PÁGINA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Login", page_icon="🔒")

# Função simples de verificação de login
def check_password():
    def password_guessed():
        if st.session_state["password"] == "admin123": # Altere sua senha aqui
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Tela de Introdução e Login
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                <div style='text-align: center; padding: 40px; background: white; border-radius: 15px; border: 2px solid #1E293B; box-shadow: 10px 10px 0px #1E293B;'>
                    <h1 style='color: #1E293B; margin-bottom: 10px;'>🚀 ExpedFlow Pro</h1>
                    <p style='color: #64748B; font-weight: bold;'>Sistema de Gestão de Notas e Fluxo de Saída</p>
                    <hr>
                    <p style='color: #000;'>Bem-vindo! Por favor, identifique-se para acessar o painel de controle.</p>
                </div>
            """, unsafe_allow_html=True)
            st.text_input("Senha de Acesso", type="password", on_change=password_guessed, key="password")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("😕 Senha incorreta.")
        return False
    return True

if not check_password():
    st.stop()

# --- 2. BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id_nota TEXT PRIMARY KEY, vendedor TEXT, obs TEXT, 
            categoria TEXT, status TEXT DEFAULT 'Inserido', 
            anexo BLOB, data_hora TEXT
        )
    ''')
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. CSS "PREMIUM DARK STEEL" (CONTRASTE MÁXIMO) ---
st.markdown("""
    <style>
    .stApp { background-color: #F1F5F9 !important; }
    
    /* Texto Preto Absoluto para não apagar */
    h1, h2, h3, p, span, label, td, th { 
        color: #000000 !important; 
        font-weight: 700 !important; 
    }

    /* Cards de Estatísticas da Intro */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #CBD5E1;
        text-align: center;
        box-shadow: 4px 4px 0px #CBD5E1;
    }

    /* Cabeçalho da Tabela */
    .table-head {
        background-color: #1E293B;
        padding: 15px;
        color: white !important;
        border-radius: 8px 8px 0 0;
        display: flex;
        justify-content: space-between;
    }
    .head-txt { color: white !important; font-size: 12px; text-transform: uppercase; }

    /* Botões */
    .stButton>button {
        border: 2px solid #000 !important;
        font-weight: 900 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DASHBOARD DE INTRODUÇÃO ---
df_intro = pd.read_sql_query("SELECT * FROM pedidos", db_conn)
total = len(df_intro)
pendentes = len(df_intro[df_intro['status'] == 'Inserido'])
concluidos = len(df_intro[df_intro['status'] == 'Finalizado'])

st.title("🏢 Painel de Controle")
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f"<div class='metric-card'>📑 Total de Notas<br><h2 style='margin:0;'>{total}</h2></div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='metric-card' style='border-color: #3B82F6;'>🔵 Pendentes<br><h2 style='margin:0;'>{pendentes}</h2></div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='metric-card' style='border-color: #22C55E;'>🟢 Finalizadas<br><h2 style='margin:0;'>{concluidos}</h2></div>", unsafe_allow_html=True)
with c4: 
    if st.button("Sair do Sistema"):
        del st.session_state["password_correct"]
        st.rerun()

st.divider()

# --- 5. INTERFACE DE LANÇAMENTO (LATERAL) ---
with st.sidebar:
    st.header("📥 Novo Registro")
    with st.form("add_form", clear_on_submit=True):
        nota = st.text_input("Nota / PDV")
        vend = st.text_input("Vendedor")
        cat = st.selectbox("Categoria", ["Mudança de Endereço", "Agendamento", "Retirada", "Aviso"])
        obs = st.text_area("Observações")
        file = st.file_uploader("Print da Nota", type=['png', 'jpg'])
        
        if st.form_submit_button("Lançar Agora", use_container_width=True):
            if nota:
                blob = file.read() if file else None
                dt = datetime.now().strftime("%d/%m %H:%M")
                db_conn.cursor().execute(
                    "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, obs, categoria, anexo, data_hora) VALUES (?,?,?,?,?,?)",
                    (nota, vend, obs, cat, blob, dt)
                )
                db_conn.commit()
                st.rerun()

# --- 6. GRID DE DADOS (VISUAL MARCOS GESTÕES) ---
search = st.text_input("🔍 Buscar Nota ou Vendedor...")
df_grid = pd.read_sql_query("SELECT * FROM pedidos ORDER BY data_hora DESC", db_conn)

if search:
    df_grid = df_grid[df_grid['id_nota'].str.contains(search) | df_grid['vendedor'].str.contains(search, case=False)]

# Cabeçalho customizado
st.markdown("""
    <div class="table-head">
        <div style="width: 10%;" class="head-txt">Nota</div>
        <div style="width: 15%;" class="head-txt">Vendedor</div>
        <div style="width: 15%;" class="head-txt">Status</div>
        <div style="width: 35%;" class="head-txt">Categoria / Detalhes</div>
        <div style="width: 10%;" class="head-txt">Print</div>
        <div style="width: 15%;" class="head-txt">Ação</div>
    </div>
    """, unsafe_allow_html=True)

for i, row in df_grid.iterrows():
    c1, c2, c3, c4, c5, c6 = st.columns([0.1, 0.15, 0.15, 0.35, 0.1, 0.15])
    
    with st.container():
        c1.markdown(f"**{row['id_nota']}**")
        c2.write(row['vendedor'])
        
        # Status
        cor_status = "#DBEAFE" if row['status'] == 'Inserido' else "#DCFCE7"
        txt_status = "#1E40AF" if row['status'] == 'Inserido' else "#166534"
        c3.markdown(f'<span style="background:{cor_status}; color:{txt_status}; padding:3px 8px; border-radius:5px; border:1px solid {txt_status}; font-size:11px;">{row["status"]}</span>', unsafe_allow_html=True)
        c3.markdown(f'<small>{row["data_hora"]}</small>', unsafe_allow_html=True)
        
        # Categoria
        c4.markdown(f"**{row['categoria']}**")
        c4.markdown(f"<small style='font-weight:normal;'>{row['obs']}</small>", unsafe_allow_html=True)
        
        # Foto
        if row['anexo']:
            if c5.button("👁️", key=f"img_{row['id_nota']}"): st.image(row['anexo'], width=400)
        else: c5.write("-")
        
        # Ações
        if row['status'] == 'Inserido':
            if c6.button("✅ Concluir", key=f"f_{row['id_nota']}", use_container_width=True):
                db_conn.cursor().execute("UPDATE pedidos SET status = 'Finalizado' WHERE id_nota = ?", (row['id_nota'],))
                db_conn.commit()
                st.rerun()
        else:
            if c6.button("🗑️ Apagar", key=f"d_{row['id_nota']}", use_container_width=True):
                db_conn.cursor().execute("DELETE FROM pedidos WHERE id_nota = ?", (row['id_nota'],))
                db_conn.commit()
                st.rerun()
    st.markdown("<hr style='margin:0; border-top: 1px solid #CBD5E1;'>", unsafe_allow_html=True)
