import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import io

# --- 1. CONFIGURAÇÃO DE ALTO NÍVEL ---
st.set_page_config(
    layout="wide", 
    page_title="ExpedFlow | Gestão Logística", 
    page_icon="🏗️",
    initial_sidebar_state="expanded"
)

# --- 2. MOTOR DE DADOS ---
def init_db():
    conn = sqlite3.connect('industria_marcos_pro.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS fluxo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pdv TEXT, loja TEXT, tipo TEXT, detalhes TEXT, 
        anexo BLOB, status TEXT DEFAULT 'Pendente', data TEXT, usuario TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT)''')
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Marcos Admin', 'Administrador')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. CSS PROFISSIONAL (DESIGN SYSTEM) ---
st.markdown("""
    <style>
    /* Importação de fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    * { font-family: 'Inter', sans-serif !important; }

    /* Fundo e Container Principal */
    .stApp { background-color: #F1F5F9 !important; }
    
    /* Sidebar Dark Mode */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        color: white !important;
    }
    section[data-testid="stSidebar"] * { color: white !important; }

    /* Cards de Resumo (KPIS) */
    .metric-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        border: 1px solid #E2E8F0;
        text-align: center;
    }

    /* Estilização dos Pedidos */
    .ticket-container {
        background-color: #FFFFFF;
        border-left: 5px solid #0F172A;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
    }

    /* Botões Profissionais */
    .stButton>button {
        background-color: #0F172A !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1E293B !important;
        transform: translateY(-1px);
    }

    /* Inputs e Forms */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
    }
    
    /* Texto em negrito forçado para visibilidade */
    b, strong, label { color: #0F172A !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. SEGURANÇA ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<div style='height:100px'></div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; color:#0F172A;'>EXPEDFLOW</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Painel Administrativo v13.0</p>", unsafe_allow_html=True)
        with st.form("login_pro"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR NO SISTEMA", use_container_width=True):
                res = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if res:
                    st.session_state.update({"auth": True, "user_name": res[0], "user_perfil": res[1]})
                    st.rerun()
                else: st.error("Acesso Negado")
    st.stop()

# --- 5. NAVEGAÇÃO LATERAL ---
with st.sidebar:
    st.markdown(f"<h2 style='margin-bottom:0;'>{st.session_state['user_name']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='opacity:0.7;'>{st.session_state['user_perfil']}</p>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("MENU PRINCIPAL", ["📊 Dashboard", "📋 Painel de Carga", "📥 Registrar Movimentação", "👥 Usuários"])
    if st.button("SAIR", use_container_width=True):
        st.session_state["auth"] = False
        st.rerun()

# --- 6. TELA: DASHBOARD (NOVIDADE) ---
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
        st.markdown(f"<div class='metric-card'><p>TOTAL HOJE</p><h2>{len(df)}</h2></div>", unsafe_allow_html=True)

# --- 7. TELA: PAINEL DE CARGA ---
elif menu == "📋 Painel de Carga":
    st.title("Controle de Fluxo")
    busca = st.text_input("🔍 Pesquisar PDV ou Loja...")
    
    df = pd.read_sql_query("SELECT * FROM fluxo ORDER BY id DESC", db_conn)
    if busca:
        df = df[df['pdv'].str.contains(busca, case=False) | df['loja'].str.contains(busca, case=False)]

    for i, r in df.iterrows():
        # Layout Estilo Ticket
        with st.container():
            st.markdown(f"""
                <div class="ticket-container">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-size: 1.2rem;"><b>PDV: {r['pdv']}</b></span>
                        <span style="background: {'#FFE4E6' if r['status'] == 'Pendente' else '#DCFCE7'}; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">
                            {r['status']}
                        </span>
                    </div>
                    <p style="margin: 10px 0;"><b>📍 Loja:</b> {r['loja']} | <b>🛠️ Tipo:</b> {r['tipo']}</p>
                    <p style="font-size: 0.9rem; color: #475569;">{r['detalhes']}</p>
                    <hr style="border: 0.1px solid #E2E8F0; margin: 10px 0;">
                    <small>📅 {r['data']} | 👤 Resp: {r['usuario']}</small>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns([0.8, 0.2])
            if r['anexo']:
                with c1.expander("📂 Ver Documento / Print"):
                    st.image(r['anexo'])
            
            if st.session_state['user_perfil'] != "Visitante" and r['status'] == 'Pendente':
                if c2.button("FINALIZAR", key=f"fin_{r['id']}", use_container_width=True):
                    db_conn.cursor().execute("UPDATE fluxo SET status='Concluído' WHERE id=?", (r['id'],))
                    db_conn.commit()
                    st.rerun()

# --- 8. TELA: REGISTRAR MOVIMENTAÇÃO ---
elif menu == "📥 Registrar Movimentação":
    st.title("Nova Movimentação")
    with st.form("form_v13"):
        c1, c2 = st.columns(2)
        f_pdv = c1.text_input("Número do PDV")
        f_loja = c2.selectbox("Origem", ["Luziânia", "Jardim Ingá", "Indústria", "Outra"])
        f_tipo = st.selectbox("Tipo de Ocorrência", ["Retirado na Indústria", "Retirada na Loja", "Cancelamento/Devolução"])
        f_det = st.text_area("Observações Técnicas")
        f_anexo = st.file_uploader("Anexar Comprovante / Print", type=['png', 'jpg', 'jpeg', 'pdf'])
        
        if st.form_submit_button("CONFIRMAR E LANÇAR", use_container_width=True):
            if f_pdv:
                blob = f_anexo.read() if f_anexo else None
                dt = datetime.now().strftime("%d/%m/%Y %H:%M")
                db_conn.cursor().execute("INSERT INTO fluxo (pdv, loja, tipo, detalhes, anexo, data, usuario) VALUES (?,?,?,?,?,?,?)",
                                       (f_pdv, f_loja, f_tipo, f_det, blob, dt, st.session_state['user_name']))
                db_conn.commit()
                st.success("Operação Registrada!")
                st.rerun()

# --- 9. TELA: USUÁRIOS ---
elif menu == "👥 Usuários":
    if st.session_state['user_perfil'] == "Administrador":
        st.title("Gestão de Acessos")
        with st.form("user_v13"):
            u_l = st.text_input("Login")
            u_n = st.text_input("Nome")
            u_s = st.text_input("Senha", type="password")
            u_p = st.selectbox("Nível", ["Administrador", "Moderador", "Loja", "Visitante"])
            if st.form_submit_button("CADASTRAR USUÁRIO"):
                db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?)", (u_l, u_s, u_n, u_p))
                db_conn.commit()
                st.success("Usuário Atualizado")
