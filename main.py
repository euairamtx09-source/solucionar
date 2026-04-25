import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Marcos Gestões - Sistema Integrado")

def init_db():
    conn = sqlite3.connect('industria_v10.db', check_same_thread=False)
    cursor = conn.cursor()
    # Tabela de Fluxo
    cursor.execute('''CREATE TABLE IF NOT EXISTS fluxo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pdv TEXT, loja TEXT, tipo TEXT, detalhes TEXT, 
        status TEXT DEFAULT 'Pendente', data TEXT, usuario TEXT)''')
    # Tabela de Usuários
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT)''')
    
    # Usuários Padrão
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Marcos Admin', 'Administrador')")
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('ira', '123', 'Irã', 'Visitante')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. CSS DE ALTO CONTRASTE (TRAVA DE CORES PARA VERCEL) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    
    /* Forçar texto PRETO ABSOLUTO em tudo */
    h1, h2, h3, p, span, label, div, b, .stMarkdown {
        color: #000000 !important;
        font-weight: 800 !important;
    }

    /* Estilo dos Cards de Pedido com Borda Grossa */
    .pedido-container {
        border: 3px solid #000000 !important;
        padding: 15px;
        background-color: #F8FAFC !important;
        border-radius: 10px;
        margin-bottom: 15px;
    }

    /* Botões Pretos com Texto Branco */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #000000;
        font-weight: bold;
    }
    
    /* Sidebar Branca */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 2px solid #000000;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONTROLE DE SESSÃO ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>MARCOS GESTÕES</h1>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                res = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if res:
                    st.session_state.update({"auth": True, "user_name": res[0], "user_perfil": res[1]})
                    st.rerun()
                else: st.error("Erro no login.")
    st.stop()

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['user_name']}")
    st.markdown(f"PERFIL: **{st.session_state['user_perfil']}**")
    st.divider()
    menu = st.radio("NAVEGAÇÃO", ["📋 PAINEL DE CARGA", "📥 REGISTRAR MOVIMENTAÇÃO", "👥 USUÁRIOS"])
    if st.button("SAIR DO APP"):
        st.session_state["auth"] = False
        st.rerun()

# --- 5. TELA: PAINEL DE CARGA ---
if menu == "📋 PAINEL DE CARGA":
    st.title("Painel de Carga")
    busca = st.text_input("🔎 BUSCAR PDV...")
    
    df = pd.read_sql_query("SELECT * FROM fluxo ORDER BY id DESC", db_conn)
    if busca: df = df[df['pdv'].str.contains(busca)]

    for i, r in df.iterrows():
        # Layout Visual do Pedido
        st.markdown(f"""
            <div style="border: 2px solid black; padding: 15px; border-radius: 8px; background: white; margin-bottom: 5px;">
                <b style="font-size: 18px; color: black;">PDV: {r['pdv']}</b> | 
                <b style="color: #1E40AF;">LOJA: {r['loja']}</b><br>
                <b style="color: #B91C1C;">OCORRÊNCIA: {r['tipo']}</b><br>
                <p style="margin: 5px 0; color: black;">DETALHES: {r['detalhes']}</p>
                <small style="color: #64748B;">Registrado: {r['data']} por {r['usuario']}</small>
            </div>
        """, unsafe_allow_html=True)
        
        # Botão de Ação
        if st.session_state["user_perfil"] != "Visitante":
            if r['status'] == 'Pendente':
                if st.button(f"DAR BAIXA NO PDV {r['pdv']}", key=f"btn_{r['id']}"):
                    db_conn.cursor().execute("UPDATE fluxo SET status='Concluído' WHERE id=?", (r['id'],))
                    db_conn.commit()
                    st.rerun()
            else:
                st.success(f"CONCLUÍDO ✅")
        st.markdown("---")

# --- 6. TELA: REGISTRAR MOVIMENTAÇÃO (COM AS NOVAS OPÇÕES) ---
elif menu == "📥 REGISTRAR MOVIMENTAÇÃO":
    if st.session_state["user_perfil"] == "Visitante":
        st.warning("Seu perfil (Visitante) não permite lançamentos.")
    else:
        st.title("Registrar Movimentação")
        with st.form("form_movimentacao", clear_on_submit=True):
            col1, col2 = st.columns(2)
            f_pdv = col1.text_input("NÚMERO DO PDV")
            f_loja = col2.selectbox("LOJA", ["Luziânia", "Jardim Ingá", "Indústria", "Outra"])
            
            # OPÇÕES ATUALIZADAS CONFORME SOLICITADO
            f_tipo = st.selectbox("OCORRÊNCIA", [
                "Retirado na Indústria", 
                "Retirada na Loja", 
                "Cancelamento/Devolução"
            ])
            
            f_det = st.text_area("DETALHES DA OCORRÊNCIA")
            
            if st.form_submit_button("LANÇAR NO PAINEL"):
                if f_pdv:
                    agora = datetime.now().strftime("%d/%m %H:%M")
                    db_conn.cursor().execute(
                        "INSERT INTO fluxo (pdv, loja, tipo, detalhes, data, usuario) VALUES (?,?,?,?,?,?)",
                        (f_pdv, f_loja, f_tipo, f_det, agora, st.session_state["user_name"])
                    )
                    db_conn.commit()
                    st.success("Lançamento realizado com sucesso!")
                else:
                    st.error("O número do PDV é obrigatório.")

# --- 7. TELA: USUÁRIOS ---
elif menu == "👥 USUÁRIOS":
    if st.session_state["user_perfil"] != "Administrador":
        st.error("Acesso restrito ao Administrador.")
    else:
        st.title("Gestão de Equipe")
        with st.form("cad_equipe"):
            u = st.text_input("USUÁRIO (LOGIN)")
            n = st.text_input("NOME COMPLETO")
            s = st.text_input("SENHA")
            p = st.selectbox("NÍVEL DE ACESSO", ["Administrador", "Moderador", "Loja", "Visitante"])
            if st.form_submit_button("CADASTRAR FUNCIONÁRIO"):
                db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?)", (u, s, n, p))
                db_conn.commit()
                st.success(f"Usuário {n} salvo!")
