import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO E BANCO DE DADOS ---
st.set_page_config(layout="wide", page_title="Indústria Integrada", page_icon="🏭")

def init_db():
    conn = sqlite3.connect('industria.db', check_same_thread=False)
    cursor = conn.cursor()
    # Tabela de Movimentações
    cursor.execute('''CREATE TABLE IF NOT EXISTS fluxo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pdv TEXT,
        loja_origem TEXT,
        tipo_acao TEXT,
        detalhes TEXT,
        foto_pedido BLOB,
        status TEXT DEFAULT 'Pendente',
        data_hora TEXT,
        responsavel TEXT
    )''')
    # Tabela de Usuários
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT
    )''')
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Gestor Indústria', 'Administrador')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. SISTEMA DE ACESSO ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h2 style='text-align:center;'>🏭 Indústria Integrada</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                res = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if res:
                    st.session_state.update({"auth": True, "user": res[0], "perfil": res[1]})
                    st.rerun()
                else: st.error("Acesso negado.")
    st.stop()

# --- 3. ESTILIZAÇÃO DE ALTO CONTRASTE ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    h1, h2, h3, p, span, label, td, th { color: #000000 !important; font-weight: 700 !important; }
    
    .status-card {
        padding: 15px; border-radius: 8px; border: 1px solid #000; margin-bottom: 10px; background: white;
    }
    .header-bar { background: #1E293B; color: white !important; padding: 10px; border-radius: 5px; display: flex; font-size: 11px; }
    .header-bar div { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. MENU LATERAL ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['user']}")
    st.info(f"Acesso: {st.session_state['user_perfil']}")
    
    aba = st.radio("Módulos", ["📋 Painel de Controle", "📥 Lançar Solicitação", "👥 Equipe"])
    
    if st.button("Sair"):
        st.session_state["auth"] = False
        st.rerun()

# --- 5. TELA: LANÇAMENTO (LOJAS E RESPONSÁVEIS) ---
if aba == "📥 Lançar Solicitação":
    st.header("Novo Chamado / Movimentação")
    
    with st.form("chamado", clear_on_submit=True):
        c1, c2 = st.columns(2)
        f_pdv = c1.text_input("Número do Pedido / PDV")
        f_tipo = c2.selectbox("Tipo de Ocorrência", [
            "Retirada de Material (Indústria)", 
            "Baixa de Expedição",
            "Devolução",
            "Cancelamento",
            "Retirada na Loja (Alteração)"
        ])
        f_obs = st.text_area("Descrição / Detalhes do Estoque")
        f_foto = st.file_uploader("Foto do Pedido (Obrigatório para Retirada)", type=['png', 'jpg', 'jpeg'])
        
        if st.form_submit_button("Enviar para a Indústria", use_container_width=True):
            if f_pdv and (f_foto or "Retirada" not in f_tipo):
                foto_bytes = f_foto.read() if f_foto else None
                dt = datetime.now().strftime("%d/%m %H:%M")
                db_conn.cursor().execute('''INSERT INTO fluxo 
                    (pdv, loja_origem, tipo_acao, detalhes, foto_pedido, data_hora, responsavel) 
                    VALUES (?,?,?,?,?,?,?)''', 
                    (f_pdv, "Luziânia", f_tipo, f_obs, foto_bytes, dt, st.session_state['user']))
                db_conn.commit()
                st.success("Solicitação enviada com sucesso!")
            else:
                st.error("Erro: Pedidos de retirada exigem foto do pedido.")

# --- 6. TELA: PAINEL DE CONTROLE (VISÃO DA INDÚSTRIA) ---
elif aba == "📋 Painel de Controle":
    st.header("Fluxo de Operação - Indústria")
    
    busca = st.text_input("🔍 Filtrar por PDV")
    
    df = pd.read_sql_query("SELECT * FROM fluxo ORDER BY id DESC", db_conn)
    if busca:
        df = df[df['pdv'].str.contains(busca)]

    # Cabeçalho
    st.markdown("""<div class='header-bar'>
        <div style='width:10%;'>PDV</div>
        <div style='width:20%;'>Tipo</div>
        <div style='width:25%;'>Detalhes/Estoque</div>
        <div style='width:15%;'>Status</div>
        <div style='width:15%;'>Foto</div>
        <div style='width:15%;'>Ação</div>
    </div>""", unsafe_allow_html=True)

    for i, r in df.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([0.1, 0.2, 0.25, 0.15, 0.15, 0.15])
        
        with st.container():
            c1.write(f"**{r['pdv']}**")
            c2.write(f"_{r['tipo_acao']}_")
            c3.write(f"<small>{r['detalhes']}</small>", unsafe_allow_html=True)
            
            # Status
            cor = "#FEF9C3" if r['status'] == 'Pendente' else "#DCFCE7"
            c4.markdown(f"<span style='background:{cor}; padding:3px 8px; border-radius:5px; border:1px solid #000; font-size:11px;'>{r['status']}</span>", unsafe_allow_html=True)
            c4.caption(r['data_hora'])
            
            # Foto
            if r['foto_pedido']:
                if c5.button("Ver Pedido", key=f"f_{r['id']}"):
                    st.image(r['foto_pedido'], caption=f"Pedido {r['pdv']}")
            else:
                c5.write("Sem foto")
            
            # Ações (Só Indústria/Admin)
            if r['status'] == 'Pendente':
                if c6.button("Finalizar", key=f"ok_{r['id']}"):
                    db_conn.cursor().execute("UPDATE fluxo SET status='Concluído' WHERE id=?", (r['id'],))
                    db_conn.commit()
                    st.rerun()
            else:
                c6.write("✅")
        st.divider()

# --- 7. TELA: EQUIPE (ADMIN) ---
elif aba == "👥 Equipe":
    if st.session_state['user_perfil'] == "Administrador":
        st.subheader("Cadastro de Funcionários")
        with st.form("user_reg"):
            nu = st.text_input("Login")
            nn = st.text_input("Nome Completo")
            ns = st.text_input("Senha")
            np = st.selectbox("Perfil", ["Visitante", "Loja", "Indústria", "Administrador"])
            if st.form_submit_button("Salvar"):
                db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?)", (nu, ns, nn, np))
                db_conn.commit()
                st.success("Usuário registrado.")
