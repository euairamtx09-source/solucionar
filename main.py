import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO E PROTEÇÃO DE SESSÃO ---
st.set_page_config(layout="wide", page_title="Marcos Gestões | ExpedFlow", page_icon="🟢")

# Inicializa variáveis de sessão para evitar KeyError
if "auth" not in st.session_state:
    st.session_state["auth"] = False
if "user_perfil" not in st.session_state:
    st.session_state["user_perfil"] = "Visitante"
if "user_name" not in st.session_state:
    st.session_state["user_name"] = "Convidado"

# --- 2. MOTOR DE DADOS ---
def init_db():
    conn = sqlite3.connect('expedflow_v20.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS fluxo (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pdv TEXT, loja TEXT, tipo TEXT, 
        detalhes TEXT, status TEXT DEFAULT 'Pendente', data TEXT, usuario TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT)''')
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Marcos Admin', 'Administrador')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. CSS PROFISSIONAL (DESIGN RETRÁTIL & CLEAN) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    
    /* Fundo e Textos */
    .stApp { background-color: #F8FAFC !important; }
    h1, h2, h3, p, label { color: #1E293B !important; }

    /* Barra Lateral Estilo 'Marcos Gestões' */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Botões da Sidebar */
    .stSidebar [data-testid="stMarkdownContainer"] p {
        color: #64748B !important;
        font-weight: 500;
    }

    /* Cards do Dashboard */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Tabela de Produção */
    .table-container {
        background: white;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
    }
    
    /* Botão Verde de Lançamento */
    div.stButton > button {
        background-color: #10B981 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
    }

    /* Esconder Erros de Sistema para o Usuário */
    .stException { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- 4. TELA DE LOGIN (PROTEGIDA) ---
if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h2 style='text-align: center;'>Marcos Gestões</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA", use_container_width=True):
                user_data = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if user_data:
                    st.session_state["auth"] = True
                    st.session_state["user_name"] = user_data[0]
                    st.session_state["user_perfil"] = user_data[1]
                    st.rerun()
                else:
                    st.error("Credenciais inválidas")
    st.stop()

# --- 5. SIDEBAR RETRÁTIL COM PERFIL ---
with st.sidebar:
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 20px;'>
            <div style='background: #10B981; padding: 10px; border-radius: 8px;'>
                <img src='https://img.icons8.com/material-rounded/24/ffffff/grid-2.png'/>
            </div>
            <h3 style='margin: 0;'>ExpedFlow</h3>
        </div>
    """, unsafe_allow_html=True)
    
    menu = st.radio("MENU PRINCIPAL", ["📊 Dashboard", "📋 Painel de Carga", "📥 Registrar", "👥 Usuários"])
    
    st.write("---")
    
    # Informações do Usuário (Rodapé da Sidebar)
    st.markdown(f"""
        <div style='padding: 10px; background: #F1F5F9; border-radius: 10px;'>
            <small style='color: #64748B; font-weight: bold;'>LOGADO COMO:</small><br>
            <span style='color: #1E293B; font-weight: 700;'>{st.session_state['user_name']}</span><br>
            <span style='color: #10B981; font-size: 12px;'>● {st.session_state['user_perfil']}</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("SAIR", use_container_width=True):
        st.session_state["auth"] = False
        st.rerun()

# --- 6. TELAS DO SISTEMA ---

if menu == "📊 Dashboard":
    st.title("Visão Geral da Operação")
    df = pd.read_sql_query("SELECT status FROM fluxo", db_conn)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='metric-card'><small>PENDENTES</small><h2>{len(df[df['status']=='Pendente'])}</h2></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><small>CONCLUÍDOS</small><h2>{len(df[df['status']=='Concluído'])}</h2></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><small>TOTAL HOJE</small><h2>{len(df)}</h2></div>", unsafe_allow_html=True)

elif menu == "📋 Painel de Carga":
    st.title("Controle de Produção")
    busca = st.text_input("🔍 Pesquisar por PDV...")
    
    # Header da Tabela
    st.markdown("""
        <div style='display: grid; grid-template-columns: 1fr 1fr 1fr 2fr 1fr; background: #1E293B; color: white; padding: 12px; border-radius: 8px 8px 0 0; font-size: 13px;'>
            <b>PDV</b> <b>LOJA</b> <b>STATUS</b> <b>DETALHES</b> <b style='text-align: right;'>AÇÃO</b>
        </div>
    """, unsafe_allow_html=True)

    df = pd.read_sql_query("SELECT * FROM fluxo ORDER BY id DESC", db_conn)
    if busca: df = df[df['pdv'].str.contains(busca, case=False)]

    for i, r in df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 2, 1])
        col1.write(f"**{r['pdv']}**")
        col2.write(r['loja'])
        
        status_color = "#FEF9C3" if r['status'] == 'Pendente' else "#DCFCE7"
        col3.markdown(f"<span style='background: {status_color}; padding: 3px 8px; border-radius: 10px; font-size: 11px;'>{r['status']}</span>", unsafe_allow_html=True)
        
        col4.write(r['detalhes'][:40] if r['detalhes'] else "-")
        
        if r['status'] == 'Pendente':
            if col5.button("Produzir", key=f"btn_{r['id']}", use_container_width=True):
                db_conn.cursor().execute("UPDATE fluxo SET status='Concluído' WHERE id=?", (r['id'],))
                db_conn.commit()
                st.rerun()
        else:
            col5.write("✅ Finalizado")
        st.markdown("<hr style='margin: 5px 0; opacity: 0.1;'>", unsafe_allow_html=True)

elif menu == "📥 Registrar":
    st.title("Nova Movimentação")
    with st.form("registro_form"):
        c1, c2 = st.columns(2)
        f_pdv = c1.text_input("Número do PDV")
        f_loja = c2.selectbox("Origem", ["Luziânia", "Jardim Ingá", "Indústria"])
        f_tipo = st.selectbox("Tipo de Ocorrência", ["Retirado na Indústria", "Retirada na Loja", "Entregar"])
        f_obs = st.text_area("Observações Técnicas")
        
        if st.form_submit_button("CONFIRMAR E LANÇAR", use_container_width=True):
            if f_pdv:
                agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                db_conn.cursor().execute("INSERT INTO fluxo (pdv, loja, tipo, detalhes, data, usuario) VALUES (?,?,?,?,?,?)",
                                       (f_pdv, f_loja, f_tipo, f_obs, agora, st.session_state['user_name']))
                db_conn.commit()
                st.success("Lançamento realizado!")
            else:
                st.error("Preencha o PDV")
