import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64
import io

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="🚚")

# --- 2. BANCO DE DADOS BLINDADO ---
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
    # RESOLUÇÃO DE BUG: Garante que a coluna 'anexo' exista se o banco for antigo
    try:
        cursor.execute("ALTER TABLE pedidos ADD COLUMN anexo BLOB")
    except:
        pass
    conn.commit()
    return conn

conn = init_db()

# --- 3. JAVASCRIPT PARA CTRL+V (ESTILO GOOGLE) ---
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
                    // Procura o input do Streamlit e injeta a imagem colada
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

# --- 4. CSS DE ALTO CONTRASTE ---
st.markdown("""
    <style>
    /* Estilo Geral */
    .stApp { background-color: #F1F3F4 !important; }
    h1, h2, h3, p, label { color: #111111 !important; font-weight: 800 !important; }
    
    /* Barra Lateral Estilo Google */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 2px solid #DADCE0;
        width: 420px !important;
    }
    section[data-testid="stSidebar"] * { color: #111111 !important; }

    /* Cards Kanban */
    .pedido-card {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #DADCE0;
        border-left: 15px solid #34A853 !important; /* Verde Forte */
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .pedido-alerta { 
        border-left: 15px solid #EA4335 !important; /* Vermelho Alerta */
        background-color: #FFF5F5 !important; 
    }

    /* Botões Grandes */
    .stButton>button {
        background-color: #1A73E8 !important;
        color: white !important;
        border-radius: 8px;
        height: 3.5em;
        width: 100%;
        font-size: 16px !important;
        border: none;
    }
    
    /* Tags de Vendedor */
    .vendedor-tag {
        background-color: #E8F0FE;
        color: #1967D2 !important;
        padding: 5px 15px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. INTERFACE PRINCIPAL ---
st.title("🚀 ExpedFlow: Controle de Carga")

with st.sidebar:
    st.header("📥 Entrada de Notas")
    
    # Área de Receptor de Imagem
    st.subheader("Anexar Print (Ctrl+V ou Arrastar)")
    arquivo_upload = st.file_uploader("Arraste aqui", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    
    # Campo de texto que recebe o Ctrl+V invisivelmente pelo JS
    buffer_colagem = st.text_input("Status do Print:", placeholder="Clique aqui e dê Ctrl+V", label_visibility="visible")
    
    final_blob = None
    if arquivo_upload:
        final_blob = arquivo_upload.read()
        st.success("✅ Arquivo pronto!")
    elif "data:image" in buffer_colagem:
        final_blob = base64.b64decode(buffer_colagem.split(",")[1])
        st.success("✅ Print colado com sucesso!")
        with st.expander("Ver Prévia"):
            st.image(final_blob)

    st.divider()

    with st.form("form_entrada", clear_on_submit=True):
        num_nota = st.text_input("Número da Nota Fiscal")
        vendedor = st.text_input("Nome do Vendedor")
        obs = st.text_area("Mudança de Endereço / Observações")
        
        btn_salvar = st.form_submit_button("CADASTRAR E SALVAR")
        
        if btn_salvar and num_nota:
            try:
                conn.cursor().execute(
                    "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, endereco, anexo, status, ultima_atualizacao) VALUES (?,?,?,?,?,?)",
                    (num_nota, vendedor, obs, final_blob, 'PENDENTE', datetime.now())
                )
                conn.commit()
                st.success("Nota salva!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")

# --- 6. EXIBIÇÃO KANBAN ---
df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY ultima_atualizacao DESC", conn)
col_mesa, col_patio = st.columns([1.5, 1])

with col_mesa:
    st.subheader("📋 FILA DA MESA (Aguardando)")
    pendentes = df[df['status'] == 'PENDENTE']
    
    for _, row in pendentes.iterrows():
        # Lógica de Alerta de Mudança
        is_alerta = any(x in str(row['endereco']).lower() for x in ['mudar', 'urgente', 'atenção', 'trocar'])
        estilo = "pedido-alerta" if is_alerta else ""
        
        with st.container():
            st.markdown(f"""
                <div class="pedido-card {estilo}">
                    <div class="vendedor-tag">Vendedor: {row['vendedor']}</div>
                    <h2 style='margin:0'>Nota: #{row['id_nota']}</h2>
                    <p style='margin-top:10px;'>{row['endereco']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if row['anexo']:
                with st.expander("🖼️ Ver Foto/Print"):
                    st.image(row['anexo'])
            
            if st.button(f"CONCLUIR CARGA #{row['id_nota']}", key=f"btn_{row['id_nota']}"):
                conn.cursor().execute("UPDATE pedidos SET status = 'CONCLUIDO' WHERE id_nota = ?", (row['id_nota'],))
                conn.commit()
                st.rerun()

with col_patio:
    st.subheader("✅ JÁ NO PÁTIO")
    concluidos = df[df['status'] == 'CONCLUIDO']
    if not concluidos.empty:
        st.table(concluidos[['id_nota', 'vendedor']].head(15))
