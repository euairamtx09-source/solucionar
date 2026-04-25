import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="🚚")

# --- 2. BANCO DE DADOS (Blindado contra erros) ---
def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id_nota TEXT PRIMARY KEY,
            vendedor TEXT,
            endereco TEXT,
            status TEXT DEFAULT 'PENDENTE',
            anexo BLOB,
            ultima_atualizacao DATETIME
        )
    ''')
    # Adiciona a coluna anexo caso o banco seja de uma versão anterior
    try:
        cursor.execute("ALTER TABLE pedidos ADD COLUMN anexo BLOB")
    except:
        pass 
    conn.commit()
    return conn

conn = init_db()

# --- 3. CSS ANTI-ESTOURO (Máxima Legibilidade) ---
st.markdown("""
    <style>
    /* Bloqueia cores de fundo e texto para evitar 'tela branca' */
    .stApp { 
        background-color: #E5E7EB !important; 
    }
    
    /* Força todo o texto para preto sólido */
    h1, h2, h3, p, span, label, li, td, th { 
        color: #000000 !important; 
        font-weight: 700 !important; 
    }

    /* Barra Lateral Estilo Google Sólida */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 3px solid #9CA3AF;
        width: 400px !important;
    }
    
    /* Inputs com bordas fortes */
    .stTextInput input, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }

    /* Cards Kanban de Alto Contraste */
    .pedido-card {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 8px;
        border: 2px solid #000000;
        border-left: 15px solid #059669 !important; /* Verde Vivo */
        margin-bottom: 15px;
        box-shadow: 4px 4px 0px #000000;
    }
    
    .pedido-alerta {
        border-left: 15px solid #DC2626 !important; /* Vermelho Vivo */
        background-color: #FEE2E2 !important;
    }

    /* Botões Grandes e Visíveis */
    .stButton>button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border: 2px solid #000000 !important;
        height: 3.5em;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. JAVASCRIPT PARA CTRL+V ---
st.markdown("""
    <script>
    const doc = window.parent.document;
    doc.addEventListener('paste', (event) => {
        const items = (event.clipboardData || event.originalEvent.clipboardData).items;
        for (const item of items) {
            if (item.kind === 'file') {
                const blob = item.getAsFile();
                const reader = new FileReader();
                reader.onload = function(e) {
                    const base64String = e.target.result;
                    const inputs = doc.querySelectorAll('input');
                    for (let input of inputs) {
                        if (input.placeholder.includes('Ctrl+V')) {
                            input.value = base64String;
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            break;
                        }
                    }
                };
                reader.readAsDataURL(blob);
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)

# --- 5. INTERFACE DO USUÁRIO ---
st.title("🚚 Painel de Expedição")

with st.sidebar:
    st.header("📥 Entrada de Notas")
    
    # Receptor de Imagem (Drag & Drop)
    arquivo_upload = st.file_uploader("Arraste o print aqui", type=['png', 'jpg', 'jpeg'])
    
    # Receptor de Imagem (Ctrl+V)
    buffer_colagem = st.text_input("Receptor de Print:", placeholder="Clique aqui e dê Ctrl+V", key="buffer_colagem")
    
    final_blob = None
    if arquivo_upload:
        final_blob = arquivo_upload.read()
        st.success("✅ Arquivo carregado!")
    elif "data:image" in buffer_colagem:
        final_blob = base64.b64decode(buffer_colagem.split(",")[1])
        st.success("✅ Print colado com sucesso!")
        with st.expander("Ver prévia do print"):
            st.image(final_blob)

    st.divider()

    with st.form("cadastro_nota", clear_on_submit=True):
        n = st.text_input("Número da NF")
        v = st.text_input("Vendedor")
        e = st.text_area("Observações/Endereço")
        if st.form_submit_button("CADASTRAR NO SISTEMA"):
            if n:
                conn.cursor().execute(
                    "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, endereco, anexo, status, ultima_atualizacao) VALUES (?,?,?,?,?,?)",
                    (n, v, e, final_blob, 'PENDENTE', datetime.now())
                )
                conn.commit()
                st.rerun()

# --- 6. EXIBIÇÃO KANBAN ---
df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY ultima_atualizacao DESC", conn)
col_mesa, col_patio = st.columns([1.5, 1])

with col_mesa:
    st.subheader("📋 FILA DE CARGA (MESA)")
    pendentes = df[df['status'] == 'PENDENTE']
    
    for _, row in pendentes.iterrows():
        # Lógica de Alerta de Mudança
        is_alerta = any(x in str(row['endereco']).lower() for x in ['mudar', 'urgente', 'atenção', 'trocar', 'erro'])
        estilo = "pedido-alerta" if is_alerta else ""
        
        with st.container():
            st.markdown(f"""
                <div class="pedido-card {estilo}">
                    <p style='margin:0; font-size:14px; text-decoration: underline;'>Vendedor: {row['vendedor']}</p>
                    <h2 style='margin:0;'>NOTA: {row['id_nota']}</h2>
                    <p style='margin-top:10px; font-size:18px;'>{row['endereco']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if row['anexo']:
                with st.expander("🖼️ Ver Foto Anexada"):
                    st.image(row['anexo'])
            
            if st.button(f"CONCLUIR #{row['id_nota']}", key=f"btn_{row['id_nota']}"):
                conn.cursor().execute("UPDATE pedidos SET status = 'CONCLUIDO', ultima_atualizacao = ? WHERE id_nota = ?", (datetime.now(), row['id_nota']))
                conn.commit()
                st.rerun()

with col_patio:
    st.subheader("✅ JÁ NO PÁTIO")
    concluidos = df[df['status'] == 'CONCLUIDO']
    if not concluidos.empty:
        # Tabela com cores sólidas
        st.dataframe(concluidos[['id_nota', 'vendedor', 'ultima_atualizacao']], use_container_width=True)
