import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO DE SEGURANÇA E PÁGINA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Enterprise", page_icon="🛡️")

def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
    # Tabela de Pedidos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id_nota TEXT PRIMARY KEY, vendedor TEXT, obs TEXT, 
            categoria TEXT, status TEXT DEFAULT 'Inserido', data_hora TEXT
        )
    ''')
    # Tabela de Usuários com PERFIL
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT
        )
    ''')
    
    # CORREÇÃO DE ERROS DE COLUNA (Auto-reparo)
    try:
        cursor.execute("SELECT perfil FROM usuarios LIMIT 1")
    except:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN perfil TEXT DEFAULT 'Visitante'")
    
    # Admin padrão
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Admin Master', 'Administrador')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. LOGIN COM NÍVEIS DE ACESSO ---
def login_screen():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        _, col, _ = st.columns([1, 1.2, 1])
        with col:
            st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
            st.markdown("""
                <div style='background: #0F172A; padding: 30px; border-radius: 15px; border: 4px solid #000; text-align: center;'>
                    <h1 style='color: white !important; margin:0;'>🛡️ EXPEDFLOW</h1>
                    <p style='color: #94A3B8 !important;'>Sistema de Gestão de Carga</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("login"):
                u = st.text_input("Usuário")
                p = st.text_input("Senha", type="password")
                if st.form_submit_button("ENTRAR NO PAINEL", use_container_width=True):
                    res = db_conn.cursor().execute(
                        "SELECT nome, perfil FROM usuarios WHERE username = ? AND password = ?", (u, p)
                    ).fetchone()
                    if res:
                        st.session_state["logged_in"] = True
                        st.session_state["user_name"] = res[0]
                        st.session_state["user_perfil"] = res[1]
                        st.rerun()
                    else: st.error("Acesso negado.")
        st.stop()

login_screen()

# --- 3. CSS DE ALTO CONTRASTE (ESTILO MARCOS GESTÕES) ---
st.markdown("""
    <style>
    .stApp { background-color: #F1F5F9 !important; }
    
    /* TRAVA DE TEXTO PRETO - Nada apaga no branco */
    h1, h2, h3, p, span, label, td, th, b, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 800 !important; 
    }

    /* Cabeçalho do Data Grid */
    .grid-header {
        background-color: #0F172A;
        padding: 15px;
        color: white !important;
        display: flex;
        justify-content: space-between;
        border-radius: 8px 8px 0 0;
        border: 1px solid #000;
    }
    .h-col { color: #FFFFFF !important; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }

    /* Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 3px solid #0F172A;
    }
    
    /* Botões Sólidos */
    .stButton>button {
        border: 2px solid #000 !important;
        background: #FFF !important;
        color: #000 !important;
        transition: 0.3s;
    }
    .stButton>button:hover { background: #000 !important; color: #FFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BARRA LATERAL E MENU ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['user_name']}")
    st.markdown(f"Nível: `{st.session_state['user_perfil']}`")
    st.divider()
    
    opcoes = ["📦 Painel de Notas"]
    if st.session_state['user_perfil'] == "Administrador":
        opcoes.append("👥 Gerenciar Usuários")
    
    menu = st.radio("Navegação Principal", opcoes)
    
    if st.button("Sair do Sistema", use_container_width=True):
        st.session_state["logged_in"] = False
        st.rerun()

# --- 5. TELA: GESTÃO DE USUÁRIOS (SÓ ADMIN) ---
if menu == "👥 Gerenciar Usuários":
    st.header("⚙️ Configuração de Acessos")
    with st.form("new_user"):
        c1, c2 = st.columns(2)
        u_log = c1.text_input("Login")
        u_nom = c2.text_input("Nome Completo")
        u_sen = c1.text_input("Senha", type="password")
        u_lev = c2.selectbox("Nível de Poder", ["Visitante", "Loja", "Moderador", "Administrador"])
        if st.form_submit_button("CRIAR NOVO USUÁRIO"):
            db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?, ?, ?, ?)", (u_log, u_sen, u_nom, u_lev))
            db_conn.commit()
            st.success("Usuário atualizado!")

# --- 6. TELA: PAINEL DE NOTAS (GRID ROBUSTO) ---
elif menu == "📦 Painel de Notas":
    st.header("🚚 Controle de Produção e Carga")
    
    # Lançamento Lateral (Apenas Loja, Moderador ou Admin)
    if st.session_state['user_perfil'] != "Visitante":
        with st.sidebar:
            st.markdown("---")
            st.subheader("📥 Novo Registro")
            with st.form("lança", clear_on_submit=True):
                n = st.text_input("Número PDV")
                v = st.text_input("Vendedor", value=st.session_state['user_name'])
                c = st.selectbox("Status Retirada", ["Entregar", "Retirar na Indústria", "Retirar na Loja"])
                o = st.text_area("Observação")
                if st.form_submit_button("SALVAR NO SISTEMA", use_container_width=True):
                    if n:
                        dt = datetime.now().strftime("%d/%m/%Y %H:%M")
                        db_conn.cursor().execute("INSERT OR REPLACE INTO pedidos (id_nota, vendedor, obs, categoria, data_hora) VALUES (?,?,?,?,?)", (n, v, o, c, dt))
                        db_conn.commit()
                        st.rerun()

    # Filtro
    busca = st.text_input("🔍 Pesquisar por PDV...", placeholder="Ex: 154594")
    
    # Carregar Dados
    df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY data_hora DESC", db_conn)
    if busca: df = df[df['id_nota'].str.contains(busca)]

    # Cabeçalho do Data Grid
    st.markdown("""
        <div class="grid-header">
            <div style="width: 15%;" class="h-col">PDV</div>
            <div style="width: 20%;" class="h-col">Loja/Vendedor</div>
            <div style="width: 20%;" class="h-col">Status</div>
            <div style="width: 30%;" class="h-col">Retirada / Obs</div>
            <div style="width: 15%;" class="h-col">Ações</div>
        </div>
    """, unsafe_allow_html=True)

    for i, row in df.iterrows():
        c1, c2, c3, c4, c5 = st.columns([0.15, 0.20, 0.20, 0.30, 0.15])
        
        with st.container():
            c1.markdown(f"<p style='font-size:18px;'>{row['id_nota']}</p>", unsafe_allow_html=True)
            c2.write(row['vendedor'])
            
            # Status Badge Dinâmico
            cor = "#CFE2FF" if row['status'] == 'Inserido' else "#D1E7DD"
            txc = "#084298" if row['status'] == 'Inserido' else "#0F5132"
            c3.markdown(f'<span style="background:{cor}; color:{txc}; padding:5px 12px; border-radius:15px; border:1px solid {txc}; font-size:12px;">{row["status"]}</span>', unsafe_allow_html=True)
            c3.markdown(f'<small>{row["data_hora"]}</small>', unsafe_allow_html=True)
            
            c4.markdown(f"**{row['categoria']}**")
            c4.markdown(f"<p style='font-weight:normal; font-size:12px;'>{row['obs']}</p>", unsafe_allow_html=True)
            
            # Ações Baseadas no Poder
            perf = st.session_state['user_perfil']
            if perf == "Visitante":
                c5.write("👁️ Somente Leitura")
            else:
                if row['status'] == 'Inserido':
                    if c5.button("✅ Concluir", key=f"ok_{row['id_nota']}", use_container_width=True):
                        db_conn.cursor().execute("UPDATE pedidos SET status = 'Finalizado' WHERE id_nota = ?", (row['id_nota'],))
                        db_conn.commit()
                        st.rerun()
                elif perf in ["Administrador", "Moderador"]:
                    if c5.button("🗑️ Apagar", key=f"del_{row['id_nota']}", use_container_width=True):
                        db_conn.cursor().execute("DELETE FROM pedidos WHERE id_nota = ?", (row['id_nota'],))
                        db_conn.commit()
                        st.rerun()
                else: c5.write("🏁 Finalizado")
        
        st.markdown("<hr style='margin:0; border-top: 1px solid #000;'>", unsafe_allow_html=True)
