import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="🚚")

# --- BANCO DE DADOS ---
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
    conn.commit()
    return conn

conn = init_db()

# --- CSS E JAVASCRIPT PARA CTRL+V ---
# Este script injeta uma lógica que escuta o evento de 'paste' (colar) no navegador
st.markdown("""
    <script>
    const doc = window.parent.document;
    doc.addEventListener('paste', (event) => {
        const items = (event.clipboardData || event.originalEvent.clipboardData).items;
        for (const item of items) {
            if (item.kind === 'file') {
                const blob = item.getAsFile();
                const reader = new FileReader();
                reader.onload = function(event) {
                    const base64String = event.target.result;
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
    <style>
    .stApp { background-color: #F3F4F6 !important; }
    .pedido-card {
        background-color: #FFFFFF !important;
        padding: 15px;
        border-radius: 10px;
        border-left: 12px solid #059669 !important;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .pedido-alerta { border-left: 12px solid #DC2626 !important; background-color: #FEF2F2 !important; }
    section[data-testid="stSidebar"] { background-color: #111827 !important; width: 400px !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚚 ExpedFlow: Painel de Controle Ágil")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📥 Entrada de Dados")
    st.write("Dica: Você pode dar **Ctrl+V** com um print aqui!")
    
    # Campo que recebe o print colado
    img_colada = st.chat_input("Ou cole o print aqui (Ctrl+V)")
    
    with st.form("cadastro_nota", clear_on_submit=True):
        n = st.text_input("Número da NF")
        v = st.text_input("Vendedor")
        e = st.text_area("Observações / Mudança")
        
        btn_salvar = st.form_submit_button("LANÇAR E SALVAR")
        
        if btn_salvar and n:
            # Converte imagem colada se existir
            img_data = None
            if img_colada and "data:image" in img_colada:
                img_data = base64.b64decode(img_colada.split(",")[1])
            
            conn.cursor().execute(
                "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, endereco, anexo, ultima_atualizacao) VALUES (?,?,?,?,?)",
                (n, v, e, img_data, datetime.now())
            )
            conn.commit()
            st.rerun()

# --- EXIBIÇÃO ---
df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY ultima_atualizacao DESC", conn)
col_mesa, col_patio = st.columns([1.5, 1])

with col_mesa:
    st.header("⏳ Notas na Mesa")
    pendentes = df[df['status'] == 'PENDENTE']
    for _, row in pendentes.iterrows():
        is_alerta = any(word in row['endereco'].lower() for word in ['mudar', 'urgente', 'trocar'])
        estilo = "pedido-alerta" if is_alerta else ""
        with st.container():
            st.markdown(f'<div class="pedido-card {estilo}"><h2>Nota #{row['id_nota']}</h2><p>{row['endereco']}</p></div>', unsafe_allow_html=True)
            if row['anexo']:
                with st.expander("🖼️ Ver Print Colado"):
                    st.image(row['anexo'])
            if st.button(f"CONCLUIR #{row['id_nota']}", key=row['id_nota']):
                conn.cursor().execute("UPDATE pedidos SET status = 'CONCLUIDO' WHERE id_nota = ?", (row['id_nota'],))
                conn.commit()
                st.rerun()

with col_patio:
    st.header("✅ Concluídas")
    st.table(df[df['status'] == 'CONCLUIDO'][['id_nota', 'vendedor']].head(10))
