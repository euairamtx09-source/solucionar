import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Marcos Gestões - Logística", page_icon="🏭")

# --- 2. BANCO DE DADOS COM SUPORTE A ANEXOS ---
def init_db():
    conn = sqlite3.connect('industria_marcos.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Tabela de Fluxo (com coluna BLOB para imagens/prints)
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
    
    # Tabela de Usuários
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        username TEXT PRIMARY KEY, 
        password TEXT, 
        nome TEXT, 
        perfil TEXT)''')
    
    # Inserção de usuários padrão
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin', 'admin123', 'Marcos Admin', 'Administrador')")
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('ira', '123', 'Irã', 'Visitante')")
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. CSS DE ALTO CONTRASTE (TRAVA DE VISIBILIDADE) ---
st.markdown("""
    <style>
    /* Força fundo branco e texto preto absoluto */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label, div, b, .stMarkdown {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    
    /* Estilização da Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 3px solid #000000;
    }

    /* Campos de entrada */
    .stTextInput>div>div>input, .stTextArea>div>textarea {
        border: 2px solid #000000 !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* Botão Principal Estilo Industrial */
    .stButton>button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 5px !important;
        font-weight: bold !important;
        border: 1px solid #000000 !important;
        height: 3em !important;
    }
    
    /* Container de Pedidos */
    .pedido-box {
        border: 2px solid #000000;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        background-color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. LÓGICA DE AUTENTICAÇÃO ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>MARCOS GESTÕES</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                res = db_conn.cursor().execute("SELECT nome, perfil FROM usuarios WHERE username=? AND password=?", (u,p)).fetchone()
                if res:
                    st.session_state.update({"auth": True, "user_name": res[0], "user_perfil": res[1]})
                    st.rerun()
                else:
                    st.error("Credenciais incorretas.")
    st.stop()

# --- 5. NAVEGAÇÃO LATERAL ---
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['user_name']}")
    st.markdown(f"Acesso: **{st.session_state['user_perfil']}**")
    st.divider()
    
    menu = st.radio("NAVEGAÇÃO", ["📋 PAINEL DE CARGA", "📥 REGISTRAR MOVIMENTAÇÃO", "👥 GERENCIAR EQUIPE"])
    
    if st.button("SAIR DO SISTEMA"):
        st.session_state["auth"] = False
        st.rerun()

# --- 6. TELA: PAINEL DE CARGA ---
if menu == "📋 PAINEL DE CARGA":
    st.title("Painel de Carga")
    busca = st.text_input("🔎 BUSCAR PDV (Ex: 12345)")
    
    df = pd.read_sql_query("SELECT * FROM fluxo ORDER BY id DESC", db_conn)
    if busca:
        df = df[df['pdv'].str.contains(busca)]

    for i, r in df.iterrows():
        # Layout em Box para garantir leitura
        st.markdown(f"""
            <div style="border: 2px solid black; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                <span style="font-size: 20px;"><b>PDV: {r['pdv']}</b></span> | <b>LOJA: {r['loja']}</b><br>
                <span style="color: #d32f2f;">TIPO: {r['tipo']}</span><br>
                <p style="margin-top: 10px;"><b>DETALHES:</b> {r['detalhes']}</p>
                <small>Registrado em: {r['data']} por {r['usuario']}</small>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns([0.7, 0.3])
        
        # Mostrar Anexo se existir
        if r['anexo']:
            with c1.expander("🖼️ VER PRINT / ARQUIVO"):
                st.image(r['anexo'])
        
        # Ações baseadas no perfil
        if st.session_state["user_perfil"] != "Visitante":
            if r['status'] == 'Pendente':
                if c2.button(f"DAR BAIXA #{r['pdv']}", key=f"bx_{r['id']}"):
                    db_conn.cursor().execute("UPDATE fluxo SET status='Concluído' WHERE id=?", (r['id'],))
                    db_conn.commit()
                    st.rerun()
            else:
                c2.success("CONCLUÍDO ✅")
        else:
            c2.info("Apenas Leitura")
        st.divider()

# --- 7. TELA: REGISTRAR MOVIMENTAÇÃO (COM ANEXOS) ---
elif menu == "📥 REGISTRAR MOVIMENTAÇÃO":
    if st.session_state["user_perfil"] == "Visitante":
        st.warning("Seu perfil não tem permissão para registrar novas movimentações.")
    else:
        st.title("Registrar Ocorrência")
        with st.form("form_registro", clear_on_submit=True):
            col1, col2 = st.columns(2)
            f_pdv = col1.text_input("NÚMERO DO PDV")
            f_loja = col2.selectbox("LOJA", ["Luziânia", "Jardim Ingá", "Indústria", "Outra"])
            
            f_tipo = st.selectbox("TIPO DE OCORRÊNCIA", [
                "Retirado na Indústria", 
                "Retirada na Loja", 
                "Cancelamento/Devolução"
            ])
            
            f_det = st.text_area("DETALHES DA OCORRÊNCIA")
            
            # Campo para Anexo (Print ou Arquivo)
            f_anexo = st.file_uploader("ANEXAR PRINT OU FOTO DO PEDIDO", type=['png', 'jpg', 'jpeg', 'pdf'])
            
            if st.form_submit_button("LANÇAR NO SISTEMA"):
                if f_pdv:
                    # Processamento do arquivo para salvar no banco
                    blob_data = f_anexo.read() if f_anexo is not None else None
                    
                    agora = datetime.now().strftime("%d/%m %H:%M")
                    db_conn.cursor().execute(
                        "INSERT INTO fluxo (pdv, loja, tipo, detalhes, anexo, data, usuario) VALUES (?,?,?,?,?,?,?)",
                        (f_pdv, f_loja, f_tipo, f_det, blob_data, agora, st.session_state["user_name"])
                    )
                    db_conn.commit()
                    st.success(f"PDV {f_pdv} registrado com sucesso!")
                else:
                    st.error("O número do PDV é obrigatório para o registro.")

# --- 8. TELA: GESTÃO DE EQUIPE (ADMIN) ---
elif menu == "👥 GERENCIAR EQUIPE":
    if st.session_state["user_perfil"] != "Administrador":
        st.error("Acesso restrito ao Administrador.")
    else:
        st.title("Controle de Usuários")
        with st.form("add_user"):
            c1, c2 = st.columns(2)
            new_u = c1.text_input("LOGIN (Usuário)")
            new_n = c2.text_input("NOME COMPLETO")
            new_s = c1.text_input("SENHA", type="password")
            new_p = c2.selectbox("PERFIL DE ACESSO", ["Administrador", "Moderador", "Loja", "Visitante"])
            
            if st.form_submit_button("CADASTRAR FUNCIONÁRIO"):
                db_conn.cursor().execute("INSERT OR REPLACE INTO usuarios VALUES (?,?,?,?)", 
                                       (new_u, new_s, new_n, new_p))
                db_conn.commit()
                st.success(f"Usuário {new_n} salvo com sucesso!")
