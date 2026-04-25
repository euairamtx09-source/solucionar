import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import io

# --- 1. CONFIGURAÇÃO DE ALTO NÍVEL ---
# Força o layout wide e define o título da aba do navegador
st.set_page_config(
    layout="wide", 
    page_title="ExpedFlow | Gestão Logística", 
    page_icon="🏗️"
)

# --- 2. MOTOR DE DADOS (CORREÇÃO DO OPERATIONALERROR) ---
def init_db():
    # Usei um nome de banco novo para garantir que ele seja criado com a estrutura correta
    conn = sqlite3.connect('expedflow_v14.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Criar tabela de fluxo com a estrutura correta (PDV, Loja, Tipo, Detalhes, Anexo, Status, Data, Usuário)
    cursor.execute('''CREATE TABLE IF NOT EXISTS fluxo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pdv TEXT, 
        loja TEXT, 
        tipo TEXT, 
        detalhes TEXT, 
        anexo BLOB, 
        status TEXT DEFAULT 'Pendente', 
        data TEXT, 
        usuario TEXT)''')
    
    # Criar tabela de usuários
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY, 
        password TEXT, 
        nome TEXT, 
        perfil TEXT)''')
    
    # Inserir usuários padrão para teste
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Marcos Admin', 'Administrador')")
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('moderador', '123', 'Airam', 'Moderador')")
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('loja', '123', 'Luziânia', 'Loja')")
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('ira', '123', 'Irã', 'Visitante')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. CSS PARA CORREÇÃO VISUAL (LETRAS INVISÍVEIS) ---
# Forçamos o tema claro, texto preto absoluto e bordas pretas nos inputs
st.markdown("""
    <style>
    /* Forçar tema claro e texto preto em tudo para evitar o erro do print */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Títulos e textos gerais em preto forte */
    h1, h2, h3, p, span, label, b, strong, .stMarkdown {
        color: #000000 !important;
        font-weight: 700 !important;
    }

    /* Estilo dos Cards do Dashboard (Estilo Marcos Gestões) */
    .metric-card {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #000000;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-card h2 { color: #1E40AF !important; font-size: 3rem !important; }
    .metric-card p { color: #000000 !important; text-transform: uppercase; font-size: 0.8rem; }

    /* Inputs e Caixas de Seleção com borda preta */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }

    /* Sidebar Dark para contraste */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    /* Botões pretos com texto branco */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. SEGURANÇA E SESSÃO (CORREÇÃO DO KEYERROR) ---
# Inicializa as variáveis de sessão para evitar erros de acesso
if "auth" not in st.session_state:
    st.session_state["auth"] = False
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""
if "user_perfil" not in st.session_state:
    st.session_state["user_perfil"] = "Visitante"

# TELA DE LOGIN (BLOQUEIA O ACESSO ÀS OUTRAS PÁGINAS)
if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h1 style='text-align:center; color:black;'>EXPEDFLOW</h1>", unsafe_allow_html=True)
        with st.form("login_v14"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR", use_container_width=True):
                # Busca usuário no banco de dados
                res = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if res:
                    st.session_state["auth"] = True
                    st.session_state["user_name"] = res[0]
                    st.session_state["user_perfil"] = res[1]
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    # Impede que o restante do código carregue se não estiver autenticado
    st.stop()

# --- 5. NAVEGAÇÃO ---
with st.sidebar:
    st.markdown(f"## 👤 {st.session_state['user_name']}")
    st.caption(f"Perfil: {st.session_state['user_perfil']}")
    st.divider()
    menu = st.radio("MENU", ["📊 Dashboard", "📋 Painel de Carga", "📥 Registrar Movimentação", "👥 Usuários"])
    if st.button("SAIR", use_container_width=True):
        st.session_state["auth"] = False
        st.rerun()

# --- 6. TELA: DASHBOARD CORRIGIDO ---
if menu == "📊 Dashboard":
    st.title("Visão Geral da Operação")
    # Tenta carregar dados. Se o banco der erro, avisa o usuário.
    try:
        df = pd.read_sql_query("SELECT * FROM fluxo", db_conn)
    except:
        st.error("Erro ao carregar banco de dados. Recarregue a página.")
        st.stop()
    
    c1, c2, c3 = st.columns(3)
    pendentes = len(df[df['status'] == 'Pendente'])
    concluidos = len(df[df['status'] == 'Concluído'])
    
    with c1:
        st.markdown(f"<div class='metric-card'><p>PENDENTES</p><h2>{pendentes}</h2></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><p>CONCLUÍDOS</p><h2>{concluidos}</h2></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><p>TOTAL GERAL</p><h2>{len(df)}</h2></div>", unsafe_allow_html=True)

# --- 7. TELA: PAINEL DE CARGA ---
elif menu == "📋 Painel de Carga":
    st.title("Controle de Chamados")
    busca = st.text_input("Filtrar por PDV...")
    
    df = pd.read_sql_query("SELECT * FROM fluxo ORDER BY id DESC", db_conn)
    if busca:
        df = df[df['pdv'].str.contains(busca, case=False)]

    if df.empty:
        st.info("Nenhum chamado registrado.")
    else:
        for i, r in df.iterrows():
            with st.container():
                # Card do Pedido com texto visível e bordas pretas
                st.markdown(f"""
                    <div style="border: 2px solid black; padding: 15px; border-radius: 8px; background: white; margin-bottom: 10px;">
                        <b style="font-size: 20px; color:black;">PDV: {r['pdv']}</b> | <b style="color:black;">LOJA: {r['loja']}</b><br>
                        <span style="color: blue;">TIPO: {r['tipo']}</span> | <b style="color:black;">STATUS: {r['status']}</b><br>
                        <p style="margin: 10px 0; color:black;">OBS: {r['detalhes'] if r['detalhes'] else 'Sem observações'}</p>
                        <small style="color:black;">Data: {r['data']} | Por: {r['usuario']}</small>
                    </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([0.7, 0.3])
                
                # Exibir Comprovante se houver
                if r['anexo']:
                    with c1.expander("🖼️ Ver Comprovante"):
                        # Supondo que seja uma imagem (BLOB)
                        st.image(r['anexo'])
                
                # Ações baseadas no poder do usuário
                if st.session_state['user_perfil'] != "Visitante" and r['status'] == 'Pendente':
                    if c2.button(f"FINALIZAR PDV {r['pdv']}", key=f"fin_{r['id']}", use_container_width=True):
                        db_conn.cursor().execute("UPDATE fluxo SET status='Concluído' WHERE id=?", (r['id'],))
                        db_conn.commit()
                        st.rerun()
            st.divider()

# --- 8. TELA: REGISTRAR MOVIMENTAÇÃO ---
elif menu == "📥 Registrar Movimentação":
    st.title("Novo Registro de Carga")
    if st.session_state['user_perfil'] == "Visitante":
        st.warning("Seu usuário não tem permissão para lançar novos chamados.")
    else:
        with st.form("form_registro", clear_on_submit=True):
            col1, col2 = st.columns(2)
            f_pdv = col1.text_input("Número do PDV")
            f_loja = col2.selectbox("Origem", ["Luziânia", "Jardim Ingá", "Indústria", "Outra"])
            
            f_tipo = st.selectbox("Ocorrência", ["Retirado na Indústria", "Retirada na Loja", "Cancelamento/Devolução"])
            f_det = st.text_area("Observações Técnicas")
            f_anexo = st.file_uploader("Anexar Comprovante / Print", type=['png', 'jpg', 'jpeg'])
            
            if st.form_submit_button("CONFIRMAR E LANÇAR", use_container_width=True):
                if f_pdv:
                    # Processamento do arquivo (BLOB)
                    blob = f_anexo.read() if f_anexo else None
                    dt = datetime.now().strftime("%d/%m/%Y %H:%M")
                    
                    try:
                        db_conn.cursor().execute(
                            "INSERT INTO fluxo (pdv, loja, tipo, detalhes, anexo, data, usuario) VALUES (?,?,?,?,?,?,?)",
                            (f_pdv, f_loja, f_tipo, f_det, blob, dt, st.session_state['user_name'])
                        )
                        db_conn.commit()
                        st.success("Lançamento Realizado com Sucesso!")
                        st.rerun()
                    except:
                        st.error("Erro ao salvar no banco de dados. Tente novamente.")
                else:
                    st.error("O número do PDV é obrigatório.")

# --- 9. USUÁRIOS (SÓ ADMIN) ---
elif menu == "👥 Usuários":
    if st.session_state['user_perfil'] != "Administrador":
        st.error("Acesso restrito ao Administrador.")
    else:
        st.title("Gestão de Equipe")
        with st.form("cad_user"):
            u_l = st.text_input("Login")
            u_n = st.text_input("Nome Completo")
            u_s = st.text_input("Senha", type="password")
            u_p = st.selectbox("Perfil de Acesso", ["Administrador", "Moderador", "Loja", "Visitante"])
            if st.form_submit_button("SALVAR USUÁRIO"):
                if u_l and u_s:
                    db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?)", (u_l, u_s, u_n, u_p))
                    db_conn.commit()
                    st.success(f"Usuário {u_n} atualizado.")
                else:
                    st.error("Login e Senha são obrigatórios.")
