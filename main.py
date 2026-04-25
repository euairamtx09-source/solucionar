import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO DE ALTO NÍVEL ---
st.set_page_config(
    layout="wide", 
    page_title="ExpedFlow Pro | Sistema de Produção",
    page_icon="🏭"
)

# --- 2. MOTOR DE DADOS (BANCO DE DADOS ROBUSTO) ---
def init_db():
    conn = sqlite3.connect('expedflow_final.db', check_same_thread=False)
    cursor = conn.cursor()
    # Tabela principal com suporte a anexo (blob)
    cursor.execute('''CREATE TABLE IF NOT EXISTS fluxo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pdv TEXT, 
        loja TEXT, 
        tipo TEXT, 
        detalhes TEXT, 
        anexo BLOB,
        status TEXT DEFAULT 'Pendente', 
        data TEXT, 
        usuario TEXT)''')
    # Tabela de usuários
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY, 
        password TEXT, 
        nome TEXT, 
        perfil TEXT)''')
    # Usuário Admin Padrão
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Marcos Admin', 'Administrador')")
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('ira', '123', 'Irã', 'Visitante')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. CSS DE ALTO CONTRASTE (TRAVA VISUAL) ---
st.markdown("""
    <style>
    /* Forçar tema claro e texto preto absoluto */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label, b, strong, th, td, .stMarkdown {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    /* Estilização da Tabela */
    .stTable { background-color: white !important; }
    
    /* Badge de Status */
    .badge {
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
    }
    .badge-pendente { background-color: #FFEB3B; color: #000 !important; }
    .badge-concluido { background-color: #4CAF50; color: #FFF !important; }

    /* Inputs com borda preta */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        border: 2px solid #000000 !important;
    }

    /* Sidebar Dark */
    section[data-testid="stSidebar"] { background-color: #0F172A !important; }
    section[data-testid="stSidebar"] * { color: #FFFFFF !important; }

    /* Botão de Ação */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 5px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. SEGURANÇA E SESSÃO ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>EXPEDFLOW PRO</h1>", unsafe_allow_html=True)
        with st.form("login_final"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR", use_container_width=True):
                res = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if res:
                    st.session_state.update({"auth": True, "user_name": res[0], "user_perfil": res[1]})
                    st.rerun()
                else: st.error("Acesso negado.")
    st.stop()

# --- 5. NAVEGAÇÃO ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['user_name']}")
    st.markdown(f"Acesso: {st.session_state['user_perfil']}")
    st.divider()
    menu = st.radio("MENU", ["📋 PAINEL DE CARGA", "📥 REGISTRAR MOVIMENTAÇÃO", "👥 EQUIPE"])
    if st.button("SAIR DO SISTEMA"):
        st.session_state["auth"] = False
        st.rerun()

# --- 6. PAINEL DE CARGA (LAYOUT DE TABELA INDUSTRIAL) ---
if menu == "📋 PAINEL DE CARGA":
    st.title("Controle de Produção")
    
    # Filtro rápido
    busca = st.text_input("🔍 Buscar PDV...")
    
    # Cabeçalho da Tabela (Em colunas)
    st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr 2fr 1.5fr; background: #000; color: #fff; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
            <div><b>PDV</b></div>
            <div><b>LOJA</b></div>
            <div><b>STATUS</b></div>
            <div><b>TIPO</b></div>
            <div><b>OBSERVAÇÃO</b></div>
            <div style="text-align: right;"><b>AÇÕES</b></div>
        </div>
    """, unsafe_allow_html=True)

    # Dados
    df = pd.read_sql_query("SELECT * FROM fluxo ORDER BY id DESC", db_conn)
    if busca:
        df = df[df['pdv'].str.contains(busca, case=False)]

    for i, r in df.iterrows():
        col_pdv, col_loja, col_status, col_tipo, col_obs, col_acoes = st.columns([1, 1, 1, 1, 2, 1.5])
        
        col_pdv.markdown(f"**{r['pdv']}**")
        col_loja.write(r['loja'])
        
        # Badge de Status
        st_color = "#FFEB3B" if r['status'] == 'Pendente' else "#4CAF50"
        st_txt = "#000" if r['status'] == 'Pendente' else "#FFF"
        col_status.markdown(f'<span style="background:{st_color}; color:{st_txt}; padding:3px 8px; border-radius:10px; font-size:11px;">{r["status"]}</span>', unsafe_allow_html=True)
        
        col_tipo.write(r['tipo'])
        col_obs.write(r['detalhes'][:30] + "..." if r['detalhes'] else "-")
        
        # Ações na direita
        if st.session_state['user_perfil'] != "Visitante":
            if r['status'] == 'Pendente':
                if col_acoes.button("✅ FINALIZAR", key=f"btn_{r['id']}", use_container_width=True):
                    db_conn.cursor().execute("UPDATE fluxo SET status='Concluído' WHERE id=?", (r['id'],))
                    db_conn.commit()
                    st.rerun()
            else:
                col_acoes.markdown('<p style="text-align:right; color:green;">OK</p>', unsafe_allow_html=True)
            
            # Se tiver anexo, mostra ícone embaixo
            if r['anexo']:
                with col_obs.expander("🖼️ Ver Print"):
                    st.image(r['anexo'])
        
        st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)

# --- 7. REGISTRAR MOVIMENTAÇÃO (COM ANEXO) ---
elif menu == "📥 REGISTRAR MOVIMENTAÇÃO":
    st.title("Lançar Ocorrência")
    if st.session_state['user_perfil'] == "Visitante":
        st.warning("Acesso apenas para leitura.")
    else:
        with st.form("registro_pro", clear_on_submit=True):
            c1, c2 = st.columns(2)
            f_pdv = c1.text_input("NÚMERO DO PDV")
            f_loja = c2.selectbox("LOJA", ["Luziânia", "Jardim Ingá", "Indústria", "Outra"])
            f_tipo = st.selectbox("OCORRÊNCIA", ["Retirado na Indústria", "Retirada na Loja", "Cancelamento/Devolução"])
            f_det = st.text_area("DETALHES")
            f_anexo = st.file_uploader("ANEXAR PRINT/FOTO", type=['png', 'jpg', 'jpeg'])
            
            if st.form_submit_button("LANÇAR NO PAINEL", use_container_width=True):
                if f_pdv:
                    blob = f_anexo.read() if f_anexo else None
                    agora = datetime.now().strftime("%d/%m %H:%M")
                    db_conn.cursor().execute("INSERT INTO fluxo (pdv, loja, tipo, detalhes, anexo, data, usuario) VALUES (?,?,?,?,?,?,?)",
                                           (f_pdv, f_loja, f_tipo, f_det, blob, agora, st.session_state['user_name']))
                    db_conn.commit()
                    st.success("Registrado!")
                    st.rerun()
                else:
                    st.error("PDV é obrigatório.")

# --- 8. EQUIPE ---
elif menu == "👥 EQUIPE":
    if st.session_state['user_perfil'] != "Administrador":
        st.error("Acesso restrito.")
    else:
        st.title("Gestão de Usuários")
        with st.form("add_equipe"):
            u = st.text_input("Login")
            n = st.text_input("Nome")
            s = st.text_input("Senha")
            p = st.selectbox("Perfil", ["Administrador", "Moderador", "Loja", "Visitante"])
            if st.form_submit_button("SALVAR"):
                db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?)", (u, s, n, p))
                db_conn.commit()
                st.success("Usuário salvo!")
