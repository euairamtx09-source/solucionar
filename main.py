import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO DE SEGURANÇA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Multi-Nível", page_icon="🔐")

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
    # Tabela de Usuários com campo de PERFIL
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT
        )
    ''')
    # Admin padrão
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Administrador Master', 'Administrador')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. LÓGICA DE AUTENTICAÇÃO ---
def login_screen():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("""
                <div style='text-align: center; padding: 25px; background: #1E293B; border-radius: 10px; border: 2px solid #000;'>
                    <h1 style='color: #FFFFFF !important;'>🛡️ ACESSO RESTRITO</h1>
                    <p style='color: #CBD5E1 !important;'>ExpedFlow Enterprise v4.0</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                u = st.text_input("Usuário")
                p = st.text_input("Senha", type="password")
                if st.form_submit_button("ENTRAR NO SISTEMA", use_container_width=True):
                    res = db_conn.cursor().execute(
                        "SELECT nome, perfil FROM usuarios WHERE username = ? AND password = ?", (u, p)
                    ).fetchone()
                    if res:
                        st.session_state["logged_in"] = True
                        st.session_state["user_name"] = res[0]
                        st.session_state["user_perfil"] = res[1]
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas.")
        st.stop()

login_screen()

# --- 3. ESTILIZAÇÃO DE ALTO CONTRASTE ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    /* Força texto preto real para não apagar */
    h1, h2, h3, p, span, label, td, th, b { color: #000000 !important; font-weight: 800 !important; }
    
    .table-head {
        background-color: #0F172A;
        padding: 12px;
        color: white !important;
        display: flex;
        justify-content: space-between;
        border-radius: 4px;
    }
    .head-txt { color: #FFFFFF !important; font-size: 11px; text-transform: uppercase; font-weight: 900; }
    
    section[data-testid="stSidebar"] { border-right: 3px solid #000; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BARRA LATERAL (MENU DINÂMICO) ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['user_name']}")
    st.markdown(f"🏅 Nível: **{st.session_state['user_perfil']}**")
    
    opcoes_menu = ["📦 Painel de Notas"]
    if st.session_state['user_perfil'] == "Administrador":
        opcoes_menu.append("⚙️ Gestão de Usuários")
    
    menu = st.radio("Navegação", opcoes_menu)
    
    if st.button("🚪 Sair do Sistema", use_container_width=True):
        st.session_state["logged_in"] = False
        st.rerun()

# --- 5. TELA: GESTÃO DE USUÁRIOS (SÓ ADMIN) ---
if menu == "⚙️ Gerenciar Usuários":
    st.header("👥 Configuração de Hierarquia")
    
    with st.form("add_user"):
        st.subheader("Novo Usuário")
        col_u, col_n = st.columns(2)
        u_login = col_u.text_input("Username")
        u_nome = col_n.text_input("Nome Completo")
        
        col_s, col_p = st.columns(2)
        u_senha = col_s.text_input("Senha", type="password")
        u_perfil = col_p.selectbox("Nível de Poder", ["Visitante", "Loja", "Moderador", "Administrador"])
        
        if st.form_submit_button("CADASTRAR USUÁRIO"):
            if u_login and u_senha:
                db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?, ?, ?, ?)", 
                                       (u_login, u_senha, u_nome, u_perfil))
                db_conn.commit()
                st.success(f"Usuário {u_nome} criado como {u_perfil}!")
            else:
                st.error("Preencha todos os campos obrigatórios.")

    st.divider()
    st.subheader("Lista de Acessos Ativos")
    usuarios_df = pd.read_sql_query("SELECT username, nome, perfil FROM usuarios", db_conn)
    st.dataframe(usuarios_df, use_container_width=True)

# --- 6. TELA: PAINEL DE NOTAS (COM PERMISSÕES) ---
elif menu == "📦 Painel de Notas":
    st.header("📋 Controle de Saída")
    
    # PERMISSÃO DE LANÇAMENTO (Só Admin, Moderador ou Loja)
    if st.session_state['user_perfil'] in ["Administrador", "Moderador", "Loja"]:
        with st.sidebar:
            st.divider()
            st.subheader("📥 Lançar Novo Pedido")
            with st.form("lança", clear_on_submit=True):
                n = st.text_input("PDV / Nota")
                v = st.text_input("Vendedor", value=st.session_state['user_name'])
                c = st.selectbox("Categoria", ["Retirada", "Agendamento", "Mudança End.", "Aviso"])
                o = st.text_area("Observação")
                if st.form_submit_button("REGISTRAR"):
                    if n:
                        dt = datetime.now().strftime("%d/%m %H:%M")
                        db_conn.cursor().execute("INSERT OR REPLACE INTO pedidos (id_nota, vendedor, obs, categoria, data_hora) VALUES (?,?,?,?,?)", (n, v, o, c, dt))
                        db_conn.commit()
                        st.rerun()
    else:
        st.sidebar.info("🚫 Seu perfil (Visitante) não permite lançamentos.")

    # GRID DE DADOS
    busca = st.text_input("🔍 Localizar Nota...")
    df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY data_hora DESC", db_conn)
    if busca: df = df[df['id_nota'].str.contains(busca)]

    # Cabeçalho do Grid (Estilo Industrial)
    st.markdown("""
        <div class="table-head">
            <div style="width: 15%;" class="head-txt">PDV</div>
            <div style="width: 20%;" class="head-txt">Vendedor</div>
            <div style="width: 20%;" class="head-txt">Status</div>
            <div style="width: 30%;" class="head-txt">Categoria / Detalhes</div>
            <div style="width: 15%;" class="head-txt">Ações</div>
        </div>
        """, unsafe_allow_html=True)

    for i, row in df.iterrows():
        c1, c2, c3, c4, c5 = st.columns([0.15, 0.20, 0.20, 0.30, 0.15])
        
        with st.container():
            c1.markdown(f"**{row['id_nota']}**")
            c2.write(row['vendedor'])
            
            # Status Badge
            cor_bg = "#DBEAFE" if row['status'] == 'Inserido' else "#DCFCE7"
            cor_tx = "#1E40AF" if row['status'] == 'Inserido' else "#166534"
            c3.markdown(f'<span style="background:{cor_bg}; color:{cor_tx}; padding:3px 8px; border-radius:5px; border:1px solid {cor_tx}; font-size:11px;">{row["status"]}</span><br><small>{row["data_hora"]}</small>', unsafe_allow_html=True)
            
            c4.markdown(f"**{row['categoria']}**")
            c4.markdown(f"<small>{row['obs']}</small>", unsafe_allow_html=True)
            
            # LÓGICA DE AÇÕES POR PODER
            perfil = st.session_state['user_perfil']
            
            if perfil == "Visitante":
                c5.write("🔒 Somente Leitura")
            else:
                if row['status'] == 'Inserido':
                    if c5.button("✅ Concluir", key=f"f_{row['id_nota']}", use_container_width=True):
                        db_conn.cursor().execute("UPDATE pedidos SET status = 'Finalizado' WHERE id_nota = ?", (row['id_nota'],))
                        db_conn.commit()
                        st.rerun()
                else:
                    # Apenas Admin e Moderador podem APAGAR registros
                    if perfil in ["Administrador", "Moderador"]:
                        if c5.button("🗑️ Apagar", key=f"d_{row['id_nota']}", use_container_width=True):
                            db_conn.cursor().execute("DELETE FROM pedidos WHERE id_nota = ?", (row['id_nota'],))
                            db_conn.commit()
                            st.rerun()
                    else:
                        c5.write("🏁 Finalizado")
        
        st.markdown("<hr style='margin:0; border-top: 1px solid #000;'>", unsafe_allow_html=True)
