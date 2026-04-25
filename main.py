import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO E SEGURANÇA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Multi-User", page_icon="👥")

def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
    # Tabela de Pedidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id_nota TEXT PRIMARY KEY, vendedor TEXT, obs TEXT, 
            categoria TEXT, status TEXT DEFAULT 'Inserido', 
            anexo BLOB, data_hora TEXT
        )
    ''')
    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY, password TEXT, nome TEXT
        )
    ''')
    # Criar usuário admin padrão se não existir
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Administrador')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. SISTEMA DE LOGIN ---
def login_screen():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("""
                <div style='text-align: center; padding: 30px; background: white; border-radius: 10px; border: 3px solid #000; box-shadow: 8px 8px 0px #000;'>
                    <h1 style='color: #000;'>🚚 EXPEDFLOW LOGIN</h1>
                    <p style='color: #333;'>Entre com suas credenciais para continuar</p>
                </div>
            """, unsafe_allow_html=True)
            
            user = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            
            if st.button("ACESSAR SISTEMA", use_container_width=True):
                res = db_conn.cursor().execute(
                    "SELECT nome FROM usuarios WHERE username = ? AND password = ?", (user, password)
                ).fetchone()
                if res:
                    st.session_state["logged_in"] = True
                    st.session_state["user_name"] = res[0]
                    st.session_state["is_admin"] = (user == 'admin')
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")
        st.stop()

login_screen()

# --- 3. ESTILIZAÇÃO DE ALTO CONTRASTE ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    h1, h2, h3, p, span, label, td, th { color: #000000 !important; font-weight: 700 !important; }
    
    /* Cabeçalho Escuro */
    .table-head {
        background-color: #000000;
        padding: 12px;
        color: white !important;
        display: flex;
        justify-content: space-between;
        border-radius: 5px 5px 0 0;
    }
    .head-txt { color: #FFFFFF !important; font-size: 11px; text-transform: uppercase; }

    /* Estilo Lateral */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 2px solid #000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MENU LATERAL E GESTÃO DE USUÁRIOS ---
with st.sidebar:
    st.markdown(f"👤 **Olá, {st.session_state['user_name']}**")
    menu = st.radio("Navegação", ["📦 Painel de Notas", "⚙️ Gerenciar Usuários"])
    
    if st.button("Sair"):
        st.session_state["logged_in"] = False
        st.rerun()

# --- 5. TELA: GERENCIAR USUÁRIOS ---
if menu == "⚙️ Gerenciar Usuários":
    st.header("👥 Gestão de Acessos")
    
    if not st.session_state["is_admin"]:
        st.warning("Apenas o administrador pode gerenciar usuários.")
    else:
        with st.form("novo_usuario"):
            st.subheader("Cadastrar Novo Usuário")
            new_u = st.text_input("Username (Login)")
            new_n = st.text_input("Nome Completo")
            new_p = st.text_input("Senha", type="password")
            if st.form_submit_button("CRIAR USUÁRIO"):
                if new_u and new_p:
                    db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?, ?, ?)", (new_u, new_p, new_n))
                    db_conn.commit()
                    st.success("Usuário criado!")
                else:
                    st.error("Preencha todos os campos.")

        st.divider()
        st.subheader("Usuários Ativos")
        users_df = pd.read_sql_query("SELECT username, nome FROM usuarios", db_conn)
        st.table(users_df)

# --- 6. TELA: PAINEL DE NOTAS (O SISTEMA PRINCIPAL) ---
elif menu == "📦 Painel de Notas":
    st.header("🚚 Controle de Expedição")
    
    # Barra lateral de lançamento (apenas se for painel de notas)
    with st.sidebar:
        st.divider()
        st.subheader("📥 Lançar Nota")
        with st.form("lançamento", clear_on_submit=True):
            f_nota = st.text_input("Número da Nota")
            f_vend = st.text_input("Vendedor")
            f_cat = st.selectbox("Categoria", ["Mudança de Endereço", "Agendamento", "Retirada", "Aviso"])
            f_obs = st.text_area("Observação")
            if st.form_submit_button("LANÇAR AGORA"):
                if f_nota:
                    dt = datetime.now().strftime("%d/%m %H:%M")
                    db_conn.cursor().execute(
                        "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, obs, categoria, data_hora) VALUES (?,?,?,?,?)",
                        (f_nota, f_vend, f_obs, f_cat, dt)
                    )
                    db_conn.commit()
                    st.rerun()

    # Filtro de Busca
    busca = st.text_input("🔍 Buscar Nota...")
    df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY data_hora DESC", db_conn)
    if busca:
        df = df[df['id_nota'].str.contains(busca)]

    # Cabeçalho do Grid
    st.markdown("""
        <div class="table-head">
            <div style="width: 15%;" class="head-txt">Nota</div>
            <div style="width: 20%;" class="head-txt">Vendedor</div>
            <div style="width: 20%;" class="head-txt">Status</div>
            <div style="width: 30%;" class="header-item head-txt">Categoria / Obs</div>
            <div style="width: 15%;" class="head-txt">Ação</div>
        </div>
        """, unsafe_allow_html=True)

    # Linhas de Dados
    for i, row in df.iterrows():
        c1, c2, c3, c4, c5 = st.columns([0.15, 0.20, 0.20, 0.30, 0.15])
        with st.container():
            c1.markdown(f"**{row['id_nota']}**")
            c2.write(row['vendedor'])
            
            # Badge Status
            cor = "#DBEAFE" if row['status'] == 'Inserido' else "#DCFCE7"
            txt = "#1E40AF" if row['status'] == 'Inserido' else "#166534"
            c3.markdown(f'<span style="background:{cor}; color:{txt}; padding:4px 10px; border-radius:5px; border:1px solid {txt}; font-size:11px;">{row["status"]}</span>', unsafe_allow_html=True)
            c3.markdown(f'<small>{row["data_hora"]}</small>', unsafe_allow_html=True)
            
            c4.markdown(f"**{row['categoria']}**")
            c4.markdown(f"<small style='font-weight:normal;'>{row['obs']}</small>", unsafe_allow_html=True)
            
            if row['status'] == 'Inserido':
                if c5.button("✅ Concluir", key=f"fin_{row['id_nota']}", use_container_width=True):
                    db_conn.cursor().execute("UPDATE pedidos SET status = 'Finalizado' WHERE id_nota = ?", (row['id_nota'],))
                    db_conn.commit()
                    st.rerun()
            else:
                if c5.button("🗑️ Apagar", key=f"del_{row['id_nota']}", use_container_width=True):
                    db_conn.cursor().execute("DELETE FROM pedidos WHERE id_nota = ?", (row['id_nota'],))
                    db_conn.commit()
                    st.rerun()
        st.markdown("<hr style='margin:0; border-top: 1px solid #000;'>", unsafe_allow_html=True)
