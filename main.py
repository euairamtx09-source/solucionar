import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURAÇÃO DE SEGURANÇA ---
st.set_page_config(layout="wide", page_title="Marcos Gestões - Indústria", page_icon="🏭")

def init_db():
    conn = sqlite3.connect('industria_v8.db', check_same_thread=False)
    cursor = conn.cursor()
    # Tabela de Fluxo (Baseada no seu grupo de WhatsApp)
    cursor.execute('''CREATE TABLE IF NOT EXISTS fluxo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pdv TEXT, loja TEXT, tipo TEXT, detalhes TEXT, 
        status TEXT DEFAULT 'Pendente', data TEXT, usuario TEXT)''')
    # Tabela de Usuários
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY, password TEXT, nome TEXT, perfil TEXT)''')
    
    # Usuário padrão para não ficar travado no login
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Marcos Admin', 'Administrador')")
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('ira', '123', 'Irã', 'Visitante')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. LÓGICA DE SESSÃO (EVITA KEYERROR) ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False
if "user_perfil" not in st.session_state:
    st.session_state["user_perfil"] = "Visitante"

# --- 3. LOGIN ---
if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h2 style='text-align:center;'>Marcos Gestões</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                res = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if res:
                    st.session_state["auth"] = True
                    st.session_state["user_name"] = res[0]
                    st.session_state["user_perfil"] = res[1]
                    st.rerun()
                else: st.error("Login inválido.")
    st.stop()

# --- 4. CSS CUSTOMIZADO (ALTO CONTRASTE) ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC !important; }
    h1, h2, h3, p, span, label, td, th, b { color: #1E293B !important; font-weight: 700 !important; }
    
    /* Botões do seu Print */
    div.stButton > button { font-weight: 700 !important; border-radius: 6px !important; }
    button[kind="secondary"] { border: 1px solid #D1D5DB !important; }
    
    /* Cores das Ações */
    .btn-produzir { background-color: #10B981 !important; color: white !important; } /* Verde */
    .btn-finalizar { background-color: #3B82F6 !important; color: white !important; } /* Azul */
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVEGAÇÃO ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state.get('user_name', 'Usuário')}")
    st.caption(f"Nível: {st.session_state.get('user_perfil', 'Visitante')}")
    st.divider()
    
    menu = st.radio("Módulos", ["📋 Painel de Produção", "📥 Novo Chamado", "👥 Administração"])
    
    if st.button("Sair"):
        st.session_state["auth"] = False
        st.rerun()

# --- 6. TELA: PAINEL DE PRODUÇÃO (ESTILO MARCOS GESTÕES) ---
if menu == "📋 Painel de Produção":
    st.title("Controle de Produção")
    st.caption("Gerencie o estoque e retiradas da indústria")
    
    busca = st.text_input("Pesquisar por PDV...", placeholder="Ex: 154594")
    
    # Carregar dados
    try:
        df = pd.read_sql_query("SELECT * FROM fluxo ORDER BY id DESC", db_conn)
    except:
        st.error("Erro ao carregar banco. Recarregue a página.")
        st.stop()

    if busca: df = df[df['pdv'].str.contains(busca)]

    # Grid de dados
    for i, r in df.iterrows():
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([0.15, 0.25, 0.25, 0.15, 0.20])
            
            c1.markdown(f"**{r['pdv']}**")
            c2.write(f"📍 {r['loja']}")
            
            # Badge de Status
            status = r['status']
            cor = "#DBEAFE" if status == 'Pendente' else "#DCFCE7"
            txt_cor = "#1E40AF" if status == 'Pendente' else "#166534"
            c3.markdown(f"<span style='background:{cor}; color:{txt_cor}; padding:4px 10px; border-radius:15px; font-size:12px;'>{status}</span>", unsafe_allow_html=True)
            c3.caption(r['data'])
            
            c4.write(f"<small>{r['tipo']}</small>", unsafe_allow_html=True)
            
            # Ações por Poder
            perfil = st.session_state["user_perfil"]
            if perfil == "Visitante":
                c5.write("👁️ Leitura")
            else:
                if status == 'Pendente':
                    if c5.button(f"▶️ Produzir", key=f"prod_{r['id']}", use_container_width=True):
                        db_conn.cursor().execute("UPDATE fluxo SET status='Produzindo' WHERE id=?", (r['id'],))
                        db_conn.commit()
                        st.rerun()
                elif status == 'Produzindo':
                    if c5.button(f"✅ Finalizar", key=f"fin_{r['id']}", use_container_width=True):
                        db_conn.cursor().execute("UPDATE fluxo SET status='Finalizado' WHERE id=?", (r['id'],))
                        db_conn.commit()
                        st.rerun()
                else:
                    c5.write("🏁 Concluído")
            
            st.markdown("<hr style='margin:5px 0; border:0.1px solid #E2E8F0;'>", unsafe_allow_html=True)

# --- 7. TELA: NOVO CHAMADO (SAIR DO WHATSAPP) ---
elif menu == "📥 Novo Chamado":
    if st.session_state["user_perfil"] == "Visitante":
        st.warning("Seu perfil não tem permissão para lançar chamados.")
    else:
        st.subheader("Substituir Mensagem do WhatsApp")
        with st.form("chamado_ind"):
            c1, c2 = st.columns(2)
            f_pdv = c1.text_input("PDV")
            f_loja = c2.selectbox("Loja", ["Luziânia", "Jardim Ingá", "Indústria"])
            f_tipo = st.selectbox("Ocorrência", ["Retirada na Indústria", "Baixa na Expedição", "Cancelamento", "Devolução"])
            f_det = st.text_area("Detalhes (Ex: Material retirado por Fulano)")
            
            if st.form_submit_button("Enviar para o Painel", use_container_width=True):
                dt = datetime.now().strftime("%d/%m %H:%M")
                db_conn.cursor().execute("INSERT INTO fluxo (pdv, loja, tipo, detalhes, data, usuario) VALUES (?,?,?,?,?,?)",
                                       (f_pdv, f_loja, f_tipo, f_det, dt, st.session_state["user_name"]))
                db_conn.commit()
                st.success("Lançado com sucesso!")

# --- 8. TELA: ADMIN ---
elif menu == "👥 Administração":
    if st.session_state["user_perfil"] != "Administrador":
        st.error("Acesso bloqueado.")
    else:
        st.subheader("Controle de Usuários")
        with st.form("add"):
            c1, c2, c3 = st.columns(3)
            u = c1.text_input("Login")
            n = c2.text_input("Nome")
            s = c3.text_input("Senha")
            p = st.selectbox("Perfil", ["Administrador", "Moderador", "Loja", "Visitante"])
            if st.form_submit_button("Cadastrar"):
                db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?)", (u, s, n, p))
                db_conn.commit()
                st.success("Usuário salvo!")
