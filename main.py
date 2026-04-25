import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import io

# --- 1. CONFIGURAÇÃO DE ALTO NÍVEL ---
st.set_page_config(
    layout="wide", 
    page_title="ExpedFlow | Gestão Logística", 
    page_icon="🏗️"
)

# --- 2. MOTOR DE DADOS (CORREÇÃO DE ERROS DE TABELA) ---
def init_db():
    # Usei um nome de arquivo novo para evitar o OperationalError de tabelas antigas
    conn = sqlite3.connect('expedflow_v14.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Criar tabela de fluxo com todas as colunas necessárias
    cursor.execute('''CREATE TABLE IF NOT EXISTS fluxo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pdv TEXT, loja TEXT, tipo TEXT, detalhes TEXT, 
        anexo BLOB, status TEXT DEFAULT 'Pendente', data TEXT, usuario TEXT)''')
    
    # Criar tabela de usuários
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT)''')
    
    # Inserir usuários padrão
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Marcos Admin', 'Administrador')")
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('ira', '123', 'Irã', 'Visitante')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. CSS PARA CORREÇÃO DE VISIBILIDADE (LETRAS INVISÍVEIS) ---
st.markdown("""
    <style>
    /* Forçar tema claro e texto preto em tudo para evitar o erro do print */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Força texto PRETO em todos os títulos e parágrafos */
    h1, h2, h3, h4, p, span, label, b, strong, .stMarkdown {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* Ajuste específico para os CARDS do Dashboard que estavam brancos no seu print */
    .metric-card {
        background-color: #F8FAFC !important;
        padding: 25px;
        border-radius: 12px;
        border: 2px solid #000000;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-card h2 { color: #1E40AF !important; font-size: 40px !important; }
    .metric-card p { color: #000000 !important; text-transform: uppercase; }

    /* Inputs e Caixas de Seleção */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }

    /* Sidebar Dark para contraste */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    /* Botão de Finalizar */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. SEGURANÇA E SESSÃO (CORREÇÃO DE KEYERROR) ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""
if "user_perfil" not in st.session_state:
    st.session_state["user_perfil"] = "Visitante"

# TELA DE LOGIN
if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>EXPEDFLOW</h1>", unsafe_allow_html=True)
        with st.form("login_v14"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR", use_container_width=True):
                res = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if res:
                    st.session_state["auth"] = True
                    st.session_state["user_name"] = res[0]
                    st.session_state["user_perfil"] = res[1]
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    st.stop()

# --- 5. NAVEGAÇÃO ---
with st.sidebar:
    st.markdown(f"## 👤 {st.session_state['user_name']}")
    st.markdown(f"Perfil: **{st.session_state['user_perfil']}**")
    st.divider()
    menu = st.radio("MENU", ["📊 Dashboard", "📋 Painel de Carga", "📥 Registrar Movimentação", "👥 Usuários"])
    if st.button("SAIR", use_container_width=True):
        st.session_state["auth"] = False
        st.rerun()

# --- 6. DASHBOARD CORRIGIDO ---
if menu == "📊 Dashboard":
    st.title("Visão Geral da Operação")
    df = pd.read_sql_query("SELECT * FROM fluxo", db_conn)
    
    c1, c2, c3 = st.columns(3)
    pendentes = len(df[df['status'] == 'Pendente'])
    concluidos = len(df[df['status'] == 'Concluído'])
    
    with c1:
        st.markdown(f"<div class='metric-card'><p>PENDENTES</p><h2>{pendentes}</h2></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><p>CONCLUÍDOS</p><h2>{concluidos}</h2></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><p>TOTAL GERAL</p><h2>{len(df)}</h2></div>", unsafe_allow_html=True)

# --- 7. PAINEL DE CARGA ---
elif menu == "📋 Painel de Carga":
    st.title("Controle de Chamados")
    busca = st.text_input("Filtrar por PDV...")
    
    df = pd.read_sql_query("SELECT * FROM fluxo ORDER BY id DESC", db_conn)
    if busca:
        df = df[df['pdv'].str.contains(busca, case=False)]

    for i, r in df.iterrows():
        with st.container():
            # Card do Pedido com texto visível
            st.markdown(f"""
                <div style="border: 2px solid black; padding: 15px; border-radius: 8px; background: white; margin-bottom: 10px;">
                    <b style="font-size: 20px;">PDV: {r['pdv']}</b> | <b>LOJA: {r['loja']}</b><br>
                    <span style="color: blue;">TIPO: {r['tipo']}</span> | <b>STATUS: {r['status']}</b><br>
                    <p style="margin: 10px 0;">OBS: {r['detalhes']}</p>
                    <small>Data: {r['data']} | Por: {r['usuario']}</small>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns([0.7, 0.3])
            if r['anexo']:
                with c1.expander("🖼️ Ver Comprovante"):
                    st.image(r['anexo'])
            
            if st.session_state['user_perfil'] != "Visitante" and r['status'] == 'Pendente':
                if c2.button(f"BAIXAR PDV {r['pdv']}", key=f"fin_{r['id']}"):
                    db_conn.cursor().execute("UPDATE fluxo SET status='Concluído' WHERE id=?", (r['id'],))
                    db_conn.commit()
                    st.rerun()
        st.divider()

# --- 8. REGISTRAR MOVIMENTAÇÃO ---
elif menu == "📥 Registrar Movimentação":
    st.title("Novo Registro")
    if st.session_state['user_perfil'] == "Visitante":
        st.warning("Seu usuário não tem permissão para lançar.")
    else:
        with st.form("form_registro", clear_on_submit=True):
            f_pdv = st.text_input("Número do PDV")
            f_loja = st.selectbox("Origem", ["Luziânia", "Jardim Ingá", "Indústria", "Outra"])
            f_tipo = st.selectbox("Ocorrência", ["Retirado na Indústria", "Retirada na Loja", "Cancelamento/Devolução"])
            f_det = st.text_area("Observações Técnicas")
            f_anexo = st.file_uploader("Anexar Print/Comprovante", type=['png', 'jpg', 'jpeg', 'pdf'])
            
            if st.form_submit_button("CONFIRMAR E LANÇAR", use_container_width=True):
                if f_pdv:
                    blob = f_anexo.read() if f_anexo else None
                    dt = datetime.now().strftime("%d/%m/%Y %H:%M")
                    db_conn.cursor().execute("INSERT INTO fluxo (pdv, loja, tipo, detalhes, anexo, data, usuario) VALUES (?,?,?,?,?,?,?)",
                                           (f_pdv, f_loja, f_tipo, f_det, blob, dt, st.session_state['user_name']))
                    db_conn.commit()
                    st.success("Lançamento Realizado!")
                else:
                    st.error("Informe o PDV.")

# --- 9. USUÁRIOS ---
elif menu == "👥 Usuários":
    if st.session_state['user_perfil'] != "Administrador":
        st.error("Acesso restrito.")
    else:
        st.title("Gestão de Equipe")
        with st.form("cad_user"):
            u_l = st.text_input("Login")
            u_n = st.text_input("Nome")
            u_s = st.text_input("Senha", type="password")
            u_p = st.selectbox("Perfil", ["Administrador", "Moderador", "Loja", "Visitante"])
            if st.form_submit_button("SALVAR"):
                db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?)", (u_l, u_s, u_n, u_p))
                db_conn.commit()
                st.success("Usuário atualizado.")
