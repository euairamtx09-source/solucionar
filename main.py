import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Marcos Gestões - Produção", page_icon="🏢")

def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Criar tabelas base
    cursor.execute('''CREATE TABLE IF NOT EXISTS pedidos 
        (id_nota TEXT PRIMARY KEY, loja TEXT, status TEXT DEFAULT 'Inserido', retirada TEXT, obs TEXT, data_hora TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
        (username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT)''')

    # AUTO-REPARO: Adicionar colunas caso não existam (Evita os erros das suas imagens)
    colunas_pedidos = [('loja', 'TEXT'), ('retirada', 'TEXT'), ('obs', 'TEXT')]
    for col, tipo in colunas_pedidos:
        try: cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {col} {tipo}")
        except: pass

    # Inserir Admin padrão
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Marcos Admin', 'Administrador')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. LOGIN COM PERMISSÕES ---
def login():
    if "auth" not in st.session_state:
        st.session_state["auth"] = False

    if not st.session_state["auth"]:
        _, col, _ = st.columns([1, 1, 1])
        with col:
            st.markdown("<h1 style='text-align:center;'>Marcos Gestões</h1>", unsafe_allow_html=True)
            with st.form("login"):
                u = st.text_input("Usuário")
                p = st.text_input("Senha", type="password")
                if st.form_submit_button("Acessar", use_container_width=True):
                    res = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                    if res:
                        st.session_state.update({"auth": True, "user": res[0], "perfil": res[1]})
                        st.rerun()
                    else: st.error("Acesso negado.")
        st.stop()

login()

# --- 3. CSS ESTILO MARCOS GESTÕES (ALTO CONTRASTE) ---
st.markdown("""
    <style>
    /* Estilo Sidebar */
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
    
    /* Texto Preto Real */
    h1, h2, p, span, label, td, th { color: #1E293B !important; font-weight: 700 !important; }
    
    /* Grid de Produção */
    .header-grid { background: #F8FAFC; padding: 10px; border-radius: 5px; border-bottom: 2px solid #CBD5E1; display: flex; text-align: center; }
    .header-item { font-size: 11px; color: #64748B !important; text-transform: uppercase; }
    
    .row-grid { background: white; padding: 15px; border-bottom: 1px solid #F1F5F9; display: flex; align-items: center; text-align: center; }
    
    /* Badges de Status */
    .badge { padding: 4px 12px; border-radius: 20px; font-size: 11px; border: 1px solid transparent; }
    .status-inserido { background: #E0F2FE; color: #0369A1 !important; border-color: #7DD3FC; }
    .status-produzindo { background: #FEF9C3; color: #854D0E !important; border-color: #FDE047; }
    .status-finalizado { background: #DCFCE7; color: #166534 !important; border-color: #86EFAC; }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVEGAÇÃO ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
    st.markdown(f"**{st.session_state['user']}**")
    st.caption(f"Nível: {st.session_state['perfil']}")
    
    menu = st.radio("Menu", ["📋 Produção", "👥 Usuários"]) if st.session_state['perfil'] == "Administrador" else "📋 Produção"
    
    if st.button("Sair"):
        st.session_state["auth"] = False
        st.rerun()

# --- 5. TELA DE USUÁRIOS (SÓ ADMIN) ---
if menu == "👥 Usuários":
    st.subheader("Gerenciar Equipe")
    with st.form("add_u"):
        c1, c2, c3 = st.columns(3)
        nu = c1.text_input("Login")
        nn = c2.text_input("Nome")
        ns = c3.text_input("Senha", type="password")
        np = st.selectbox("Poder", ["Visitante", "Loja", "Moderador", "Administrador"])
        if st.form_submit_button("Criar Usuário"):
            db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?)", (nu, ns, nn, np))
            db_conn.commit()
            st.success("Usuário salvo.")

# --- 6. TELA DE PRODUÇÃO ---
else:
    st.title("Controle de Produção")
    st.caption("Gerencie seus pedidos de forma eficiente")

    # Lançamento (Visível para Loja, Moderador e Admin)
    if st.session_state['perfil'] != "Visitante":
        with st.expander("➕ Novo Pedido"):
            with st.form("novo_p", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                f_pdv = c1.text_input("PDV")
                f_loja = c2.text_input("Loja/Vendedor", value="Luziânia")
                f_ret = c3.selectbox("Retirada", ["Entregar", "Retirar na indústria", "Retirar na Loja"])
                f_obs = st.text_area("Observação")
                if st.form_submit_button("Lançar"):
                    dt = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                    db_conn.cursor().execute("INSERT INTO pedidos (id_nota, loja, retirada, obs, data_hora) VALUES (?,?,?,?,?)", (f_pdv, f_loja, f_ret, f_obs, dt))
                    db_conn.commit()
                    st.rerun()

    # Filtro
    busca = st.text_input("Pesquisar por PDV...", placeholder="Ex: 154594")
    df = pd.read_sql_query("SELECT * FROM pedidos", db_conn)
    if busca: df = df[df['id_nota'].str.contains(busca)]

    # Cabeçalho
    st.markdown("""<div class='header-grid'>
        <div style='width:15%;' class='header-item'>PDV</div>
        <div style='width:15%;' class='header-item'>Loja</div>
        <div style='width:20%;' class='header-item'>Status</div>
        <div style='width:20%;' class='header-item'>Retirada</div>
        <div style='width:15%;' class='header-item'>Observação</div>
        <div style='width:15%;' class='header-item'>Ações</div>
    </div>""", unsafe_allow_html=True)

    # Linhas
    for i, r in df.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([0.15, 0.15, 0.20, 0.20, 0.15, 0.15])
        
        c1.markdown(f"**{r['id_nota']}**")
        c2.write(r['loja'])
        
        # Badge de Status
        st_class = "status-inserido" if r['status'] == 'Inserido' else "status-produzindo" if r['status'] == 'Produzindo' else "status-finalizado"
        c3.markdown(f"<span class='badge {st_class}'>{r['status']}<br><small>{r['data_hora']}</small></span>", unsafe_allow_html=True)
        
        c4.write(r['retirada'])
        c5.write(r['obs'] if r['obs'] else "-")
        
        # Ações por Nível de Poder
        perfil = st.session_state['perfil']
        if perfil == "Visitante":
            c6.write("🔒")
        else:
            if r['status'] == 'Inserido':
                if c6.button("🔨 Produzir", key=f"p_{r['id_nota']}"):
                    db_conn.cursor().execute("UPDATE pedidos SET status='Produzindo' WHERE id_nota=?", (r['id_nota'],))
                    db_conn.commit()
                    st.rerun()
            elif r['status'] == 'Produzindo':
                if c6.button("✅ Finalizar", key=f"f_{r['id_nota']}"):
                    db_conn.cursor().execute("UPDATE pedidos SET status='Finalizado' WHERE id_nota=?", (r['id_nota'],))
                    db_conn.commit()
                    st.rerun()
            
            # Só Admin e Moderador podem Apagar
            if perfil in ["Administrador", "Moderador"]:
                if c6.button("🗑️", key=f"d_{r['id_nota']}"):
                    db_conn.cursor().execute("DELETE FROM pedidos WHERE id_nota=?", (r['id_nota'],))
                    db_conn.commit()
                    st.rerun()
        st.divider()
