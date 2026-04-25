import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO E PROTEÇÃO ---
st.set_page_config(layout="wide", page_title="ExpedFlow | Marcos Gestões", page_icon="🟢")

if "auth" not in st.session_state: st.session_state["auth"] = False
if "user_name" not in st.session_state: st.session_state["user_name"] = "Convidado"

# --- 2. MOTOR DE DADOS ---
def init_db():
    conn = sqlite3.connect('expedflow_v21.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS fluxo (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pdv TEXT, loja TEXT, tipo TEXT, 
        detalhes TEXT, status TEXT DEFAULT 'Pendente', data TEXT, usuario TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT)''')
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Marcos Gestões', 'Administrador')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. CSS DESIGN (ESTILO MARCOS GESTÕES) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; color: #1E293B; }
    
    .stApp { background-color: #F8FAFC !important; }

    /* Estilo do Botão Principal (Verde) */
    div.stButton > button:first-child {
        background-color: #10B981 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 10px 24px !important;
    }

    /* Tabela / Cards */
    .table-header {
        background: #0F172A;
        color: white !important;
        padding: 15px;
        border-radius: 8px 8px 0 0;
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 2fr 1fr;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .table-header div { color: white !important; }

    /* Barra Lateral */
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIN ---
if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h2 style='text-align: center;'>ExpedFlow</h2>", unsafe_allow_html=True)
        with st.form("login_v21"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("Acessar", use_container_width=True):
                user = db_conn.cursor().execute("SELECT nome FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if user:
                    st.session_state.update({"auth": True, "user_name": user[0]})
                    st.rerun()
    st.stop()

# --- 5. SIDEBAR (REDUZIDA) ---
with st.sidebar:
    st.markdown("### 🟢 ExpedFlow")
    menu = st.radio("Navegação", ["📋 Painel de Carga", "📊 Dashboard", "👥 Usuários"])
    st.divider()
    st.caption(f"Usuário: {st.session_state['user_name']}")
    if st.button("Sair", use_container_width=True):
        st.session_state["auth"] = False
        st.rerun()

# --- 6. TELA: PAINEL DE CARGA (COM "NOVO PEDIDO" INTEGRADO) ---
if menu == "📋 Painel de Carga":
    st.title("Painel de Carga")
    
    # --- ÁREA DE AÇÃO (O QUE VOCÊ PEDIU) ---
    col_busca, col_vazio, col_btn = st.columns([3, 4, 2])
    busca = col_busca.text_input("🔍 Buscar PDV...", label_visibility="collapsed", placeholder="Pesquisar PDV...")
    
    # BOTÃO PARA ABRIR FORMULÁRIO
    with col_btn:
        expandir_form = st.expander("➕ NOVO PEDIDO", expanded=False)
    
    with expandir_form:
        st.markdown("#### Detalhes do Novo Registro")
        with st.form("form_integrado", clear_on_submit=True):
            c1, c2 = st.columns(2)
            f_pdv = c1.text_input("Número do PDV")
            f_loja = c2.selectbox("Loja", ["Luziânia", "Jardim Ingá", "Indústria"])
            f_tipo = st.selectbox("Tipo de Movimentação", ["Retirar na Indústria", "Retirar na Loja", "Entrega Pendente"])
            f_obs = st.text_area("Observações")
            
            if st.form_submit_button("SALVAR E LANÇAR NO PAINEL", use_container_width=True):
                if f_pdv:
                    agora = datetime.now().strftime("%d/%m %H:%M")
                    db_conn.cursor().execute("INSERT INTO fluxo (pdv, loja, tipo, detalhes, data, usuario) VALUES (?,?,?,?,?,?)",
                                           (f_pdv, f_loja, f_tipo, f_obs, agora, st.session_state['user_name']))
                    db_conn.commit()
                    st.success(f"PDV {f_pdv} lançado!")
                    st.rerun()
                else:
                    st.error("Informe o PDV.")

    st.divider()

    # --- TABELA DE CARGA ---
    st.markdown("""
        <div class="table-header">
            <div>PDV</div>
            <div>Loja</div>
            <div>Status</div>
            <div>Tipo/Obs</div>
            <div style="text-align: right;">Ação</div>
        </div>
    """, unsafe_allow_html=True)

    df = pd.read_sql_query("SELECT * FROM fluxo ORDER BY id DESC", db_conn)
    if busca: df = df[df['pdv'].str.contains(busca, case=False)]

    for i, r in df.iterrows():
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 2, 1])
        c1.markdown(f"**{r['pdv']}**")
        c2.write(r['loja'])
        
        # Status
        status_bg = "#FEF9C3" if r['status'] == 'Pendente' else "#DCFCE7"
        c3.markdown(f"<span style='background:{status_bg}; padding:4px 10px; border-radius:12px; font-size:12px;'>{r['status']}</span>", unsafe_allow_html=True)
        
        c4.write(f"*{r['tipo']}* — {r['detalhes'][:30] if r['detalhes'] else ''}")
        
        # Botão de Ação
        if r['status'] == 'Pendente':
            if c5.button("Finalizar", key=f"f_{r['id']}", use_container_width=True):
                db_conn.cursor().execute("UPDATE fluxo SET status='Concluído' WHERE id=?", (r['id'],))
                db_conn.commit()
                st.rerun()
        else:
            c5.markdown("<p style='text-align:right; color:#10B981;'>✅</p>", unsafe_allow_html=True)
        
        st.markdown("<hr style='margin:5px 0; opacity:0.1'>", unsafe_allow_html=True)

# --- 7. TELA: DASHBOARD ---
elif menu == "📊 Dashboard":
    st.title("Resumo da Operação")
    df = pd.read_sql_query("SELECT status FROM fluxo", db_conn)
    st.metric("Total de Pedidos", len(df))
    st.metric("Pendentes", len(df[df['status']=='Pendente']))

# --- 8. TELA: USUÁRIOS ---
elif menu == "👥 Usuários":
    st.title("Gestão de Acesso")
    with st.form("add_user"):
        u = st.text_input("Usuário")
        s = st.text_input("Senha")
        if st.form_submit_button("Cadastrar"):
            db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios (username, password, nome, perfil) VALUES (?,?,'Novo','Operador')", (u,s))
            db_conn.commit()
            st.success("Usuário Atualizado!")
