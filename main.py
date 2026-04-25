import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(
    layout="wide", 
    page_title="ExpedFlow | Gestão", 
    page_icon="🟢",
    initial_sidebar_state="expanded"
)

# --- 2. MOTOR DE DADOS ---
def init_db():
    conn = sqlite3.connect('expedflow_v19.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS fluxo (
        id INTEGER PRIMARY KEY AUTOINCREMENT, pdv TEXT, loja TEXT, tipo TEXT, 
        detalhes TEXT, status TEXT DEFAULT 'Pendente', data TEXT, usuario TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT)''')
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Marcos Gestões', 'admin')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. CSS PARA UI/UX (O SEGREDO DO LAYOUT) ---
st.markdown("""
    <style>
    /* 1. Cores e Fontes Estilo 'Marcos Gestões' */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC !important; }

    /* 2. Customização da Sidebar Retrátil */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
        width: 260px !important;
    }
    
    /* 3. Estilização dos Itens do Menu (Lado Esquerdo) */
    .menu-item {
        display: flex;
        align-items: center;
        padding: 12px 15px;
        border-radius: 8px;
        margin-bottom: 5px;
        color: #64748B;
        text-decoration: none;
        transition: all 0.3s;
    }
    .menu-item:hover {
        background-color: #F1F5F9;
        color: #10B981;
    }
    .active-menu {
        background-color: #ECFDF5 !important;
        color: #10B981 !important;
        font-weight: 600;
    }

    /* 4. Tabela Estilo Dashboard */
    .custom-table {
        width: 100%;
        background: white;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        overflow: hidden;
    }
    
    /* 5. Cabeçalho da Tabela */
    .table-header {
        background-color: #F8FAFC;
        padding: 15px;
        display: grid;
        grid-template-columns: 1fr 1fr 1.5fr 1fr 2fr 1fr;
        font-weight: 700;
        color: #475569;
        font-size: 13px;
        border-bottom: 1px solid #E2E8F0;
    }

    /* 6. Linha da Tabela */
    .table-row {
        padding: 15px;
        display: grid;
        grid-template-columns: 1fr 1fr 1.5fr 1fr 2fr 1fr;
        align-items: center;
        border-bottom: 1px solid #F1F5F9;
        transition: 0.2s;
    }
    .table-row:hover { background-color: #FDFDFD; }

    /* 7. Badges de Status */
    .badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        text-align: center;
        width: fit-content;
    }
    .badge-pendente { background: #FEF9C3; color: #A16207; }
    .badge-produzindo { background: #DBEAFE; color: #1E40AF; }
    .badge-concluido { background: #DCFCE7; color: #15803D; }

    /* 8. Botão Novo Pedido (Verde) */
    .stButton>button {
        background-color: #10B981 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIN ---
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.image("https://cdn-icons-png.flaticon.com/512/1063/1063376.png", width=80)
        st.markdown("### Bem-vindo ao ExpedFlow")
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                res = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if res:
                    st.session_state.update({"auth": True, "user_name": res[0], "user_perfil": res[1]})
                    st.rerun()
    st.stop()

# --- 5. SIDEBAR (MENU RETRÁTIL IDENTICO AO PRINT) ---
with st.sidebar:
    # Cabeçalho do Menu
    st.markdown("""
        <div style='display: flex; align-items: center; margin-bottom: 30px;'>
            <div style='background: #10B981; padding: 8px; border-radius: 8px; margin-right: 10px;'>
                <img src='https://img.icons8.com/material-rounded/24/ffffff/grid-2.png'/>
            </div>
            <h3 style='margin: 0; color: #1E293B;'>Marcos Gestões</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Navegação com ícones
    menu = st.radio(
        "Navegação",
        ["Dashboard", "Todos os Pedidos", "Registrar", "Equipe"],
        label_visibility="collapsed"
    )
    
    st.spacer = st.container() # Empurrar perfil para o fundo
    for _ in range(15): st.write("") 

    # Perfil do Usuário no rodapé da sidebar
    st.markdown(f"""
        <div style='border-top: 1px solid #E2E8F0; padding-top: 20px;'>
            <div style='display: flex; align-items: center;'>
                <img src='https://img.icons8.com/color/48/000000/user-male-circle--v1.png' width='40'/>
                <div style='margin-left: 10px;'>
                    <b style='color: #1E293B; display: block;'>{st.session_state['user_name']}</b>
                    <small style='color: #64748B;'>{st.session_state['user_perfil']}</small>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state["auth"] = False
        st.rerun()

# --- 6. TELAS ---

if menu == "Dashboard":
    st.markdown("## Dashboard")
    df = pd.read_sql_query("SELECT status FROM fluxo", db_conn)
    c1, c2, c3 = st.columns(3)
    c1.metric("Pendentes", len(df[df['status']=='Pendente']))
    c2.metric("Concluídos", len(df[df['status']=='Concluído']))
    c3.metric("Total Hoje", len(df))

elif menu == "Todos os Pedidos":
    st.markdown("## Controle de Produção")
    st.caption("Gerencie seus pedidos de forma eficiente")
    
    col_busca, _, col_btn = st.columns([4, 4, 2])
    busca = col_busca.text_input("🔍 Pesquisar por PDV...", label_visibility="collapsed")
    
    # Tabela Profissional
    st.markdown("""
        <div class='table-header'>
            <div>PDV</div>
            <div>LOJA</div>
            <div>STATUS</div>
            <div>RETIRADA</div>
            <div>OBSERVAÇÃO</div>
            <div style='text-align: right;'>AÇÕES</div>
        </div>
    """, unsafe_allow_html=True)
    
    df = pd.read_sql_query("SELECT * FROM fluxo ORDER BY id DESC", db_conn)
    if busca: df = df[df['pdv'].str.contains(busca, case=False)]

    for i, r in df.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1.5, 1, 2, 1])
        
        c1.markdown(f"**{r['pdv']}**")
        c2.write(r['loja'])
        
        # Status com Cor
        badge_style = "badge-pendente" if r['status'] == 'Pendente' else "badge-concluido"
        c3.markdown(f"<div class='badge {badge_style}'>{r['status']}</div>", unsafe_allow_html=True)
        
        c4.write(r['tipo'])
        c5.write(r['detalhes'][:30] if r['detalhes'] else "-")
        
        # Ações
        if r['status'] == 'Pendente':
            if c6.button("Produzir", key=f"p_{r['id']}"):
                db_conn.cursor().execute("UPDATE fluxo SET status='Concluído' WHERE id=?", (r['id'],))
                db_conn.commit()
                st.rerun()
        else:
            c6.write("✅")
        st.markdown("<hr style='margin:0; opacity:0.1'>", unsafe_allow_html=True)

elif menu == "Registrar":
    st.markdown("## Novo Pedido")
    with st.form("reg"):
        p = st.text_input("Número do PDV")
        l = st.selectbox("Loja", ["Luziânia", "Jardim Ingá", "Indústria"])
        t = st.selectbox("Tipo", ["Entregar", "Retirar na Indústria", "Retirar na Loja"])
        o = st.text_area("Observações")
        if st.form_submit_button("Lançar"):
            dt = datetime.now().strftime("%d/%m/%Y %H:%M")
            db_conn.cursor().execute("INSERT INTO fluxo (pdv, loja, tipo, detalhes, data, usuario) VALUES (?,?,?,?,?,?)",
                                   (p, l, t, o, dt, st.session_state['user_name']))
            db_conn.commit()
            st.success("Lançado!")
