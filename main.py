import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO E PROTEÇÃO DE SESSÃO (SESSION GUARD) ---
st.set_page_config(layout="wide", page_title="Marcos Gestões | ExpedFlow", page_icon="🟢")

if "auth" not in st.session_state:
    st.session_state["auth"] = False
if "user_perfil" not in st.session_state:
    st.session_state["user_perfil"] = "Operador"
if "user_name" not in st.session_state:
    st.session_state["user_name"] = "Convidado"

# --- 2. MOTOR DE DADOS ---
def init_db():
    conn = sqlite3.connect('expedflow_v25.db', check_same_thread=False)
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

# --- 3. CSS DESIGN (ESTILO MODERNO & RESTRITO) ---
# O uso de strings triplas f""" evita o SyntaxError: invalid decimal literal
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    * {{ font-family: 'Inter', sans-serif; }}
    
    .stApp {{ background-color: #F8FAFC !important; }}
    
    /* Cabeçalho da Tabela */
    .table-header {{
        background-color: #1E293B;
        color: white !important;
        padding: 15px;
        border-radius: 10px 10px 0 0;
        display: grid;
        grid-template-columns: 1fr 1fr 1fr 2fr 1fr;
        font-weight: 600;
        font-size: 13px;
    }}

    /* Botão Novo Pedido (Verde) */
    div.stButton > button:first-child {{
        background-color: #10B981 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }}

    /* Cards */
    .metric-card {{
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        text-align: center;
    }}
    
    /* Esconder erros técnicos do usuário final */
    .stException {{ display: none; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. TELA DE LOGIN ---
if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h2 style='text-align: center;'>Marcos Gestões</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR NO SISTEMA", use_container_width=True):
                user_data = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if user_data:
                    st.session_state["auth"] = True
                    st.session_state["user_name"] = user_data[0]
                    st.session_state["user_perfil"] = user_data[1]
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🟢 ExpedFlow")
    menu = st.radio("NAVEGAÇÃO", ["📋 Painel de Carga", "📊 Dashboard", "⚙️ Configurações"])
    
    st.markdown("---")
    st.markdown(f"**Usuário:** {st.session_state['user_name']}")
    st.caption(f"Perfil: {st.session_state['user_perfil']}")
    
    if st.button("Logout", use_container_width=True):
        st.session_state["auth"] = False
        st.rerun()

# --- 6. PAINEL DE CARGA (INTEGRADO COM NOVO PEDIDO) ---
if menu == "📋 Painel de Carga":
    st.title("Painel de Carga")

    # Layout Superior: Busca e Botão Novo
    col_busca, col_vazio, col_btn = st.columns([3, 3, 2])
    busca = col_busca.text_input("🔍 Buscar PDV...", placeholder="Digite o número do PDV...")
    
    # Botão que expande o formulário de novo pedido
    with col_btn:
        novo_pedido_expander = st.expander("➕ NOVO PEDIDO", expanded=False)

    with novo_pedido_expander:
        with st.form("form_novo_pedido", clear_on_submit=True):
            st.subheader("Registrar Movimentação")
            c1, c2 = st.columns(2)
            f_pdv = c1.text_input("Número do PDV")
            f_loja = c2.selectbox("Origem/Loja", ["Luziânia", "Jardim Ingá", "Indústria", "Valparaíso"])
            f_tipo = st.selectbox("O que deve ser feito?", ["Retirar na Indústria", "Entrega Pendente", "Retirada na Loja", "Troca"])
            f_obs = st.text_area("Observações e Detalhes")
            
            if st.form_submit_button("SALVAR PEDIDO", use_container_width=True):
                if f_pdv:
                    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
                    db_conn.cursor().execute(
                        "INSERT INTO fluxo (pdv, loja, tipo, detalhes, data, usuario) VALUES (?,?,?,?,?,?)",
                        (f_pdv, f_loja, f_tipo, f_obs, data_hora, st.session_state['user_name'])
                    )
                    db_conn.commit()
                    st.success(f"PDV {f_pdv} inserido com sucesso!")
                    st.rerun()
                else:
                    st.error("O campo PDV é obrigatório.")

    st.markdown("---")

    # Cabeçalho Estilizado da Tabela
    st.markdown("""
        <div class="table-header">
            <div>PDV</div>
            <div>LOJA</div>
            <div>STATUS</div>
            <div>DETALHES</div>
            <div style="text-align: right;">AÇÕES</div>
        </div>
    """, unsafe_allow_html=True)

    # Lógica de Busca e Listagem
    query = "SELECT * FROM fluxo ORDER BY id DESC"
    df = pd.read_sql_query(query, db_conn)
    
    if busca:
        df = df[df['pdv'].astype(str).str.contains(busca)]

    for _, row in df.iterrows():
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 2, 1])
        
        c1.write(f"**{row['pdv']}**")
        c2.write(row['loja'])
        
        # Status Colorido
        cor_status = "#FEF9C3" if row['status'] == 'Pendente' else "#DCFCE7"
        c3.markdown(f"<span style='background:{cor_status}; padding:3px 10px; border-radius:10px; font-size:12px;'>{row['status']}</span>", unsafe_allow_html=True)
        
        c4.write(f"{row['tipo']} | {row['detalhes'][:30]}...")
        
        # Botão de Ação (Apenas se Pendente)
        if row['status'] == 'Pendente':
            if c5.button("Concluir", key=f"f_{row['id']}", use_container_width=True):
                db_conn.cursor().execute("UPDATE fluxo SET status='Concluído' WHERE id=?", (row['id'],))
                db_conn.commit()
                st.rerun()
        else:
            c5.write("✅ Finalizado")
        
        st.markdown("<hr style='margin:5px 0; opacity:0.1'>", unsafe_allow_html=True)

# --- 7. DASHBOARD ---
elif menu == "📊 Dashboard":
    st.title("Indicadores de Desempenho")
    df = pd.read_sql_query("SELECT status FROM fluxo", db_conn)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Pedidos", len(df))
    col2.metric("Pendentes", len(df[df['status']=='Pendente']))
    col3.metric("Finalizados", len(df[df['status']=='Concluído']))
    
    st.bar_chart(df['status'].value_counts())

# --- 8. CONFIGURAÇÕES (GESTÃO DE USUÁRIOS) ---
elif menu == "⚙️ Configurações":
    st.title("Configurações do Sistema")
    if st.session_state["user_perfil"] == "Administrador":
        with st.form("add_user"):
            st.subheader("Cadastrar Novo Usuário")
            new_u = st.text_input("Login")
            new_p = st.text_input("Senha", type="password")
            new_n = st.text_input("Nome Completo")
            new_perf = st.selectbox("Perfil", ["Operador", "Administrador"])
            if st.form_submit_button("CADASTRAR"):
                db_conn.cursor().execute("INSERT INTO usuarios VALUES (?,?,?,?)", (new_u, new_p, new_n, new_perf))
                db_conn.commit()
                st.success("Usuário criado!")
    else:
        st.warning("Apenas administradores podem gerenciar usuários.")
