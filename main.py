import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from PIL import Image

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="🚚")

# --- BANCO DE DADOS (Atualizado para suportar anexos) ---
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

# --- CSS DE ALTO CONTRASTE ---
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
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚚 ExpedFlow: Painel Operacional")

# --- BARRA LATERAL: ÁREA DE IMPORTAÇÃO E CADASTRO ---
with st.sidebar:
    st.header("📥 Entrada de Dados")
    
    # Opção 1: Importar Arquivo/Print
    st.subheader("Anexar Documento ou Print")
    arquivo_upload = st.file_uploader("Arraste o print ou arquivo aqui", type=['png', 'jpg', 'jpeg', 'pdf'])
    
    st.divider()
    
    # Opção 2: Formulário Manual
    st.subheader("Dados da Nota")
    with st.form("cadastro_nota", clear_on_submit=True):
        n = st.text_input("Número da NF")
        v = st.text_input("Vendedor")
        e = st.text_area("Observações / Mudança de Endereço")
        
        btn_salvar = st.form_submit_button("LANÇAR NO SISTEMA")
        
        if btn_salvar and n:
            img_byte = arquivo_upload.read() if arquivo_upload else None
            try:
                conn.cursor().execute(
                    "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, endereco, anexo, ultima_atualizacao) VALUES (?,?,?,?,?)",
                    (n, v, e, img_byte, datetime.now())
                )
                conn.commit()
                st.success(f"Nota {n} registrada!")
                st.rerun()
            except Exception as ex:
                st.error(f"Erro ao salvar: {ex}")

# --- CORPO DO SISTEMA ---
df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY ultima_atualizacao DESC", conn)
col_mesa, col_patio = st.columns([1.5, 1])

with col_mesa:
    st.header("⏳ Notas na Mesa")
    pendentes = df[df['status'] == 'PENDENTE']
    
    for _, row in pendentes.iterrows():
        is_alerta = any(word in row['endereco'].lower() for word in ['mudar', 'urgente', 'trocar', 'atenção'])
        estilo = "pedido-alerta" if is_alerta else ""
        
        with st.container():
            st.markdown(f"""
                <div class="pedido-card {estilo}">
                    <p style='color: #1E40AF !important; font-size: 12px;'>Vendedor: {row['vendedor']}</p>
                    <h2 style='margin: 0;'>Nota #{row['id_nota']}</h2>
                    <p style='margin-top: 10px;'>{row['endereco']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Se houver anexo/print, mostra um botão para ver
            if row['anexo']:
                with st.expander("🖼️ Ver Print/Anexo"):
                    st.image(row['anexo'])
            
            if st.button(f"CONCLUIR CARGA #{row['id_nota']}", key=f"btn_{row['id_nota']}"):
                conn.cursor().execute("UPDATE pedidos SET status = 'CONCLUIDO' WHERE id_nota = ?", (row['id_nota'],))
                conn.commit()
                st.rerun()

with col_patio:
    st.header("✅ Concluídas")
    concluidos = df[df['status'] == 'CONCLUIDO']
    st.table(concluidos[['id_nota', 'vendedor']].head(15))
