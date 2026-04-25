import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="🚚")

# --- BANCO DE DADOS (Com correção para KeyError) ---
def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
    # Criar tabela se não existir
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
    # Tenta adicionar a coluna anexo caso o banco seja antigo
    try:
        cursor.execute("ALTER TABLE pedidos ADD COLUMN anexo BLOB")
    except:
        pass # Coluna já existe
    conn.commit()
    return conn

conn = init_db()

# --- MÁGICA DO CTRL + V (JavaScript) ---
# Esse script captura o evento de colar e joga o dado para um componente do Streamlit
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
                    // Encontra o input de texto do Streamlit para injetar o valor ou usa o postMessage
                    window.parent.postMessage({
                        type: 'streamlit:set_component_value',
                        value: base64String
                    }, '*');
                };
                reader.readAsDataURL(blob);
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)

# --- ESTILO DE ALTO CONTRASTE ---
st.markdown("""
    <style>
    .stApp { background-color: #F3F4F6 !important; }
    h1, h2, h3, p, label { color: #111827 !important; font-weight: 700 !important; }
    .pedido-card {
        background-color: #FFFFFF !important;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #E5E7EB;
        border-left: 12px solid #059669 !important;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .pedido-alerta { border-left: 12px solid #DC2626 !important; background-color: #FEF2F2 !important; }
    section[data-testid="stSidebar"] { background-color: #111827 !important; width: 400px !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚚 ExpedFlow: Painel Operacional")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📥 Entrada de Dados")
    
    # Este campo captura o Base64 enviado pelo JavaScript acima
    colagem_data = st.text_input("Status do Print:", placeholder="Aguardando Ctrl+V...", key="buffer_colagem")
    
    if "data:image" in colagem_data:
        st.success("✅ Imagem capturada!")
        with st.expander("Prévia do Print"):
            st.image(colagem_data)
    
    st.divider()
    
    with st.form("cadastro_agil", clear_on_submit=True):
        n = st.text_input("Número da Nota")
        v = st.text_input("Vendedor")
        e = st.text_area("Observações / Mudanças")
        
        btn = st.form_submit_button("LANÇAR NO SISTEMA")
        
        if btn and n:
            img_blob = None
            if "data:image" in colagem_data:
                img_blob = base64.b64decode(colagem_data.split(",")[1])
            
            conn.cursor().execute(
                "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, endereco, anexo, status, ultima_atualizacao) VALUES (?,?,?,?,?,?)",
                (n, v, e, img_blob, 'PENDENTE', datetime.now())
            )
            conn.commit()
            st.success("Salvo!")
            st.rerun()

# --- EXIBIÇÃO ---
df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY ultima_atualizacao DESC", conn)
col_mesa, col_patio = st.columns([1.5, 1])

with col_mesa:
    st.header("⏳ Notas na Mesa")
    pendentes = df[df['status'] == 'PENDENTE']
    for _, row in pendentes.iterrows():
        is_alerta = any(w in str(row['endereco']).lower() for w in ['mudar', 'urgente', 'trocar'])
        estilo = "pedido-alerta" if is_alerta else ""
        with st.container():
            st.markdown(f'<div class="pedido-card {estilo}"><p>Vendedor: {row["vendedor"]}</p><h2 style="margin:0">Nota #{row["id_nota"]}</h2><p>{row["endereco"]}</p></div>', unsafe_allow_html=True)
            
            if row['anexo']:
                with st.expander("🖼️ Ver Print Anexado"):
                    st.image(row['anexo'])
            
            if st.button(f"CONCLUIR #{row['id_nota']}", key=f"c_{row['id_nota']}"):
                conn.cursor().execute("UPDATE pedidos SET status = 'CONCLUIDO' WHERE id_nota = ?", (row['id_nota'],))
                conn.commit()
                st.rerun()

with col_patio:
    st.header("✅ Concluídas")
    st.table(df[df['status'] == 'CONCLUIDO'][['id_nota', 'vendedor']].head(10))
