import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import io

# --- 1. CONFIGURAÇÃO DE ALTO NÍVEL ---
st.set_page_config(
    layout="wide", 
    page_title="ExpedFlow Pro | Sistema de Produção",
    page_icon="🏭"
)

# --- 2. MOTOR DE DADOS (ESTRUTURA FINAL) ---
def init_db():
    conn = sqlite3.connect('expedflow_v18_final.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS fluxo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pdv TEXT, loja TEXT, tipo TEXT, detalhes TEXT, 
        anexo BLOB, status TEXT DEFAULT 'Pendente', data TEXT, usuario TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT)''')
    # Usuário Mestre
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Marcos Admin', 'Administrador')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. CSS DESIGN SYSTEM (MARKDOWN + TABELA + VISIBILIDADE) ---
st.markdown("""
    <style>
    /* Reset de Fundo e Texto */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Estilização de Títulos e Textos Markdown */
    h1 {
        color: #0F172A !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        border-bottom: 3px solid #0F172A;
        padding-bottom: 5px;
    }
    
    strong, b, label {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* Layout de Tabela Industrial */
    .header-table {
        background-color: #0F172A;
        color: white;
        padding: 12px;
        border-radius: 5px 5px 0 0;
        display: grid;
        grid-template-columns: 1fr 1fr 1.5fr 1fr 2fr 1.5fr;
        font-weight: bold;
        font-size: 0.9rem;
    }

    .row-table {
        display: grid;
        grid-template-columns: 1fr 1fr 1.5fr 1fr 2fr 1.5fr;
        padding: 10px;
        border-bottom: 1px solid #E2E8F0;
        align-items: center;
        background: white;
    }

    /* Badges de Status */
    .status-pill {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
        text-transform: uppercase;
    }

    /* Sidebar Dark */
    section[data-testid="stSidebar"] { background-color: #0F172A !important; }
    section[data-testid="stSidebar"] * { color: #FFFFFF !important; }

    /* Botões */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 5px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. SEGURANÇA ---
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("# ACESSO EXPEDFLOW")
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR", use_container_width=True):
                res = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if res:
                    st.session_state.update({"auth": True, "user_name": res[0], "user_perfil": res[1]})
                    st.rerun()
                else: st.error("Erro de login.")
    st.stop()

# --- 5. NAVEGAÇÃO ---
with st.sidebar:
    st.markdown(f"## {st.session_state['user_name']}")
    st.markdown(f"*{st.session_state['user_perfil']}*")
    st.divider()
    menu = st.radio("MENU", ["📋 Painel de Carga", "📥 Novo Registro", "👥 Equipe"])
    if st.button("SAIR"):
        st.session_state["auth"] = False
        st.rerun()

# --- 6. PAINEL DE CARGA (O LAYOUT SOLICITADO) ---
if menu == "📋 Painel de Carga":
    st.markdown("# Controle de Produção")
    
    col_f, _ = st.columns([2, 3])
    busca = col_f.text_input("🔍 Buscar PDV...")

    # Cabeçalho Estilizado
    st.markdown("""
        <div class="header-table">
            <div>PDV</div>
            <div>LOJA</div>
            <div>STATUS</div>
            <div>RETIRADA</div>
            <div>DETALHES</div>
            <div style="text-align: right;">AÇÕES</div>
        </div>
    """, unsafe_allow_html=True)

    df = pd.read_sql_query("SELECT * FROM fluxo ORDER BY id DESC", db_conn)
    if busca: df = df[df['pdv'].str.contains(busca, case=False)]

    for i, r in df.iterrows():
        c_pdv, c_loja, c_status, c_tipo, c_obs, c_btn = st.columns([1, 1, 1.5, 1, 2, 1.5])
        
        c_pdv.markdown(f"**{r['pdv']}**")
        c_loja.write(r['loja'])
        
        # Badge de Status
        cor_fundo = "#FEF9C3" if r['status'] == 'Pendente' else "#DCFCE7"
        cor_texto = "#854D0E" if r['status'] == 'Pendente' else "#166534"
        c_status.markdown(f'<span class="status-pill" style="background:{cor_fundo}; color:{cor_texto};">{r["status"]}</span>', unsafe_allow_html=True)
        
        c_tipo.write(r['tipo'])
        
        # Seção de detalhes + anexo
        with c_obs:
            st.write(r['detalhes'] if r['detalhes'] else "-")
            if r['anexo']:
                with st.expander("📁 Ver Print"):
                    st.image(r['anexo'])

        # Botão de Ação na Direita
        if r['status'] == 'Pendente' and st.session_state['user_perfil'] != "Visitante":
            if c_btn.button("FINALIZAR", key=f"f_{r['id']}", use_container_width=True):
                db_conn.cursor().execute("UPDATE fluxo SET status='Concluído' WHERE id=?", (r['id'],))
                db_conn.commit()
                st.rerun()
        else:
            c_btn.markdown('<p style="text-align:right; color:#166534; font-size:12px;">CONCLUÍDO</p>', unsafe_allow_html=True)
        
        st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)

# --- 7. NOVO REGISTRO ---
elif menu == "📥 Novo Registro":
    st.markdown("# Nova Movimentação")
    if st.session_state['user_perfil'] == "Visitante":
        st.warning("Seu perfil permite apenas visualização.")
    else:
        with st.form("reg_final", clear_on_submit=True):
            col1, col2 = st.columns(2)
            f_pdv = col1.text_input("Número do PDV")
            f_loja = col2.selectbox("Loja Destino", ["Luziânia", "Jardim Ingá", "Indústria", "Outra"])
            f_tipo = st.selectbox("Tipo de Ocorrência", ["Retirado na Indústria", "Retirada na Loja", "Cancelamento/Devolução"])
            f_det = st.text_area("Observações Adicionais")
            f_anexo = st.file_uploader("Anexar Print/Documento", type=['png', 'jpg', 'jpeg'])
            
            if st.form_submit_button("LANÇAR NO SISTEMA", use_container_width=True):
                if f_pdv:
                    blob = f_anexo.read() if f_anexo else None
                    dt = datetime.now().strftime("%d/%m %H:%M")
                    db_conn.cursor().execute("INSERT INTO fluxo (pdv, loja, tipo, detalhes, anexo, data, usuario) VALUES (?,?,?,?,?,?,?)",
                                           (f_pdv, f_loja, f_tipo, f_det, blob, dt, st.session_state['user_name']))
                    db_conn.commit()
                    st.success("Lançamento concluído!")
                else:
                    st.error("PDV é obrigatório.")

# --- 8. EQUIPE ---
elif menu == "👥 Equipe":
    if st.session_state['user_perfil'] != "Administrador":
        st.error("Acesso restrito.")
    else:
        st.markdown("# Gestão de Usuários")
        with st.form("add_user"):
            u_l = st.text_input("Login")
            u_n = st.text_input("Nome Completo")
            u_s = st.text_input("Senha")
            u_p = st.selectbox("Perfil", ["Administrador", "Moderador", "Loja", "Visitante"])
            if st.form_submit_button("CADASTRAR"):
                db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?)", (u_l, u_s, u_n, u_p))
                db_conn.commit()
                st.success("Usuário atualizado.")
