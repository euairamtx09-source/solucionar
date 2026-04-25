import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Marcos Gestões", page_icon="🏢")

# --- 2. BANCO DE DADOS COM REPARO AUTOMÁTICO ---
def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Criar tabelas se não existirem
    cursor.execute('''CREATE TABLE IF NOT EXISTS pedidos 
        (id_nota TEXT PRIMARY KEY, loja TEXT, status TEXT DEFAULT 'Inserido', retirada TEXT, obs TEXT, data_hora TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
        (username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT)''')

    # FIX PARA DatabaseError: Verifica e adiciona colunas faltantes em 'usuarios'
    cursor.execute("PRAGMA table_info(usuarios)")
    cols_user = [info[1] for info in cursor.fetchall()]
    if 'perfil' not in cols_user:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN perfil TEXT DEFAULT 'Visitante'")
    if 'nome' not in cols_user:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN nome TEXT")

    # FIX PARA OperationalError: Verifica e adiciona colunas em 'pedidos'
    cursor.execute("PRAGMA table_info(pedidos)")
    cols_ped = [info[1] for info in cursor.fetchall()]
    for c in ['loja', 'retirada', 'obs', 'data_hora']:
        if c not in cols_ped:
            cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {c} TEXT")

    # Garante um administrador inicial
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Marcos Admin', 'Administrador')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. LOGIN ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>🔐 Acesso Restrito</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                res = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if res:
                    st.session_state.update({"auth": True, "user": res[0], "perfil": res[1]})
                    st.rerun()
                else: st.error("Usuário ou senha incorretos.")
    st.stop()

# --- 4. CSS (VISUAL "MARCOS GESTÕES" - ALTO CONTRASTE) ---
st.markdown("""
    <style>
    /* Estilo do Fundo e Sidebar */
    .stApp { background-color: #F9FAFB !important; }
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E5E7EB; }
    
    /* Força Texto Preto para não sumir no branco */
    h1, h2, h3, p, span, label, td, th { color: #111827 !important; font-weight: 700 !important; }
    
    /* Grid Estilizado */
    .header-bar { background: #1F2937; color: white !important; padding: 12px; border-radius: 8px 8px 0 0; display: flex; font-size: 11px; text-transform: uppercase; font-weight: 900; }
    .header-bar div { color: white !important; }
    
    /* Badges de Status (Cores Fortes) */
    .st-badge { padding: 4px 10px; border-radius: 6px; font-size: 11px; border: 1px solid #000; font-weight: bold; }
    .status-inserido { background-color: #DBEAFE; color: #1E40AF !important; }
    .status-produzindo { background-color: #FEF9C3; color: #854D0E !important; }
    .status-finalizado { background-color: #DCFCE7; color: #166534 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVEGAÇÃO LATERAL ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['user']}")
    st.markdown(f"Nível: **{st.session_state['perfil']}**")
    
    menu_items = ["📋 Painel de Produção"]
    if st.session_state['perfil'] == "Administrador":
        menu_items.append("👥 Gestão de Equipe")
    
    menu = st.radio("Navegação", menu_items)
    
    if st.button("Sair"):
        st.session_state["auth"] = False
        st.rerun()

# --- 6. TELA: GESTÃO DE EQUIPE (ADMIN) ---
if menu == "👥 Gestão de Equipe":
    st.title("Gerenciar Usuários")
    with st.form("cad_user"):
        c1, c2, c3 = st.columns(3)
        nu = c1.text_input("Login")
        nn = c2.text_input("Nome")
        ns = c3.text_input("Senha", type="password")
        np = st.selectbox("Perfil de Poder", ["Visitante", "Loja", "Moderador", "Administrador"])
        if st.form_submit_button("Salvar Usuário"):
            db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?)", (nu, ns, nn, np))
            db_conn.commit()
            st.success("Usuário atualizado com sucesso!")

# --- 7. TELA: PAINEL DE PRODUÇÃO ---
else:
    st.title("Controle de Produção")
    
    # Botão Novo Pedido (Só Loja, Moderador ou Admin)
    if st.session_state['perfil'] != "Visitante":
        with st.expander("➕ Cadastrar Novo PDV"):
            with st.form("novo_pdv", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                f_pdv = c1.text_input("Número PDV")
                f_loja = c2.text_input("Loja/Cidade", value="Luziânia")
                f_ret = c3.selectbox("Tipo de Saída", ["Entregar", "Retirar na Indústria", "Retirar na Loja"])
                f_obs = st.text_area("Observações Adicionais")
                if st.form_submit_button("Confirmar Lançamento"):
                    dt = datetime.now().strftime("%d/%m/%y %H:%M")
                    db_conn.cursor().execute("INSERT OR REPLACE INTO pedidos (id_nota, loja, retirada, obs, data_hora) VALUES (?,?,?,?,?)", (f_pdv, f_loja, f_ret, f_obs, dt))
                    db_conn.commit()
                    st.rerun()

    # Filtro de Busca
    busca = st.text_input("🔍 Pesquisar por PDV...", placeholder="Digite o número da nota")
    df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY data_hora DESC", db_conn)
    if busca: df = df[df['id_nota'].str.contains(busca)]

    # Cabeçalho da Tabela
    st.markdown("""<div class='header-bar'>
        <div style='width:15%;'>PDV</div>
        <div style='width:15%;'>Loja</div>
        <div style='width:20%;'>Status Atual</div>
        <div style='width:20%;'>Logística</div>
        <div style='width:15%;'>OBS</div>
        <div style='width:15%;'>Ações</div>
    </div>""", unsafe_allow_html=True)

    # Dados
    for i, r in df.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([0.15, 0.15, 0.20, 0.20, 0.15, 0.15])
        
        c1.markdown(f"**{r['id_nota']}**")
        c2.write(r['loja'])
        
        # Status Dinâmico
        s = r['status']
        cl = "status-inserido" if s == 'Inserido' else "status-produzindo" if s == 'Produzindo' else "status-finalizado"
        c3.markdown(f"<span class='st-badge {cl}'>{s}</span><br><small>{r['data_hora']}</small>", unsafe_allow_html=True)
        
        c4.write(r['retirada'])
        c5.write(r['obs'] if r['obs'] else "-")
        
        # Botões por Poder
        p = st.session_state['perfil']
        if p == "Visitante":
            c6.write("🔒")
        else:
            if s == 'Inserido':
                if c6.button("🔨 Produzir", key=f"p_{r['id_nota']}", use_container_width=True):
                    db_conn.cursor().execute("UPDATE pedidos SET status='Produzindo' WHERE id_nota=?", (r['id_nota'],))
                    db_conn.commit()
                    st.rerun()
            elif s == 'Produzindo':
                if c6.button("✅ Finalizar", key=f"f_{r['id_nota']}", use_container_width=True):
                    db_conn.cursor().execute("UPDATE pedidos SET status='Finalizado' WHERE id_nota=?", (r['id_nota'],))
                    db_conn.commit()
                    st.rerun()
            
            if p in ["Administrador", "Moderador"]:
                if c6.button("🗑️", key=f"d_{r['id_nota']}", use_container_width=True):
                    db_conn.cursor().execute("DELETE FROM pedidos WHERE id_nota=?", (r['id_nota'],))
                    db_conn.commit()
                    st.rerun()
        st.markdown("<hr style='margin:5px 0; border:0.5px solid #E5E7EB;'>", unsafe_allow_html=True)
