import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Marcos Gestões - Visibilidade Total")

def init_db():
    conn = sqlite3.connect('industria_final.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS fluxo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pdv TEXT, loja TEXT, tipo TEXT, detalhes TEXT, 
        status TEXT DEFAULT 'Pendente', data TEXT, usuario TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT)''')
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Marcos Admin', 'Administrador')")
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('ira', '123', 'Irã', 'Visitante')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. CSS DE ALTO CONTRASTE (TRAVA DE CORES) ---
# Aqui garantimos que o fundo é sempre claro e a letra sempre PRETA
st.markdown("""
    <style>
    /* Fundo Global */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Forçar TODAS as letras para PRETO */
    h1, h2, h3, h4, h5, h6, p, li, span, label, div {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* Input Fields (Onde digita) */
    input, textarea, select {
        background-color: #F1F5F9 !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }

    /* Sidebar (Menu Lateral) */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 2px solid #E2E8F0;
    }
    
    /* Estilo dos Cards de Pedido */
    .pedido-container {
        background-color: #FFFFFF;
        border: 2px solid #000000;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }

    /* Botão Primário */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 5px;
        font-weight: bold;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE ACESSO ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>LOGÍSTICA MARCOS</h1>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR"):
                res = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if res:
                    st.session_state.update({"auth": True, "user_name": res[0], "user_perfil": res[1]})
                    st.rerun()
                else: st.error("Usuário ou senha incorretos.")
    st.stop()

# --- 4. INTERFACE PRINCIPAL ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['user_name']}")
    st.markdown(f"Nível: **{st.session_state['user_perfil']}**")
    st.divider()
    menu = st.radio("MENU", ["📋 PAINEL DE CARGA", "📥 NOVO CHAMADO", "👥 USUÁRIOS"])
    if st.button("SAIR"):
        st.session_state["auth"] = False
        st.rerun()

# --- 5. PAINEL DE CARGA ---
if menu == "📋 PAINEL DE CARGA":
    st.title("Painel de Carga e Retirada")
    busca = st.text_input("🔎 BUSCAR PDV...")
    
    df = pd.read_sql_query("SELECT * FROM fluxo ORDER BY id DESC", db_conn)
    if busca: df = df[df['pdv'].str.contains(busca)]

    for i, r in df.iterrows():
        # Container com borda preta para garantir visibilidade
        st.markdown(f"""
            <div style="border: 2px solid black; padding: 10px; border-radius: 8px; background: white; margin-bottom: 10px;">
                <b style="font-size: 20px;">PDV: {r['pdv']}</b> | <span>Loja: {r['loja']}</span><br>
                <span style="color: blue;">Ação: {r['tipo']}</span><br>
                <p style="margin: 5px 0;">Detalhes: {r['detalhes']}</p>
                <small>Registrado em: {r['data']}</small>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns([0.8, 0.2])
        status = r['status']
        perfil = st.session_state["user_perfil"]
        
        if perfil != "Visitante":
            if status == 'Pendente':
                if c2.button(f"CONCLUIR #{r['pdv']}", key=f"f_{r['id']}"):
                    db_conn.cursor().execute("UPDATE fluxo SET status='Concluído' WHERE id=?", (r['id'],))
                    db_conn.commit()
                    st.rerun()
            else:
                c2.success("BAIXA OK")

# --- 6. NOVO CHAMADO ---
elif menu == "📥 NOVO CHAMADO":
    if st.session_state["user_perfil"] == "Visitante":
        st.warning("Acesso apenas para leitura.")
    else:
        st.subheader("Registrar Movimentação (Saída do WhatsApp)")
        with st.form("add_chamado"):
            f_pdv = st.text_input("Número do PDV")
            f_loja = st.selectbox("Loja", ["Luziânia", "Jardim Ingá", "Indústria"])
            f_tipo = st.selectbox("Ocorrência", ["Retirada Material", "Baixa Expedição", "Cancelamento"])
            f_det = st.text_area("Descrição do que ocorreu")
            if st.form_submit_button("ENVIAR PARA INDÚSTRIA"):
                dt = datetime.now().strftime("%d/%m %H:%M")
                db_conn.cursor().execute("INSERT INTO fluxo (pdv, loja, tipo, detalhes, data, usuario) VALUES (?,?,?,?,?,?)",
                                       (f_pdv, f_loja, f_tipo, f_det, dt, st.session_state["user_name"]))
                db_conn.commit()
                st.success("Lançado!")

# --- 7. USUÁRIOS ---
elif menu == "👥 USUÁRIOS":
    if st.session_state["user_perfil"] != "Administrador":
        st.error("Acesso negado.")
    else:
        st.subheader("Controle de Equipe")
        with st.form("cad"):
            u = st.text_input("Login")
            n = st.text_input("Nome")
            s = st.text_input("Senha")
            p = st.selectbox("Perfil", ["Administrador", "Moderador", "Loja", "Visitante"])
            if st.form_submit_button("CADASTRAR"):
                db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?)", (u, s, n, p))
                db_conn.commit()
                st.success("Salvo!")
