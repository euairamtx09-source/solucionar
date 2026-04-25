import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64

# --- CONFIGURAÇÃO DA PÁGINA (Layout Largo e Profissional) ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="📑")

# --- BANCO DE DADOS (Blindado contra DatabaseError) ---
def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
    # Criamos a tabela com as colunas necessárias para evitar KeyError
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id_nota TEXT PRIMARY KEY,
            vendedor TEXT,
            obs TEXT,
            categoria TEXT,
            status TEXT DEFAULT 'Inserido',
            anexo BLOB,
            data_hora DATETIME
        )
    ''')
    conn.commit()
    return conn

conn = init_db()

# --- CSS PERSONALIZADO (Inspirado na imagem image_5c9db0.png) ---
st.markdown("""
    <style>
    /* Estilo do Fundo e Container Principal */
    .stApp { background-color: #F4F7F6 !important; }
    
    /* Menu Lateral Branco e Limpo */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E0E0E0;
    }
    
    /* Títulos em Preto para Contraste */
    h1, h2, h3, p, span, label { color: #333333 !important; font-weight: 600 !important; }

    /* Badges de Status (Cores da imagem enviada) */
    .status-badge {
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: bold;
        display: inline-block;
    }
    .status-inserido { background-color: #E3F2FD; color: #1976D2; }
    .status-finalizado { background-color: #E8F5E9; color: #2E7D32; }

    /* Estilo de Categoria */
    .cat-tag {
        font-size: 12px;
        color: #666;
        background: #F1F1F1;
        padding: 2px 8px;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (CADASTRO) ---
with st.sidebar:
    st.title("📦 ExpedFlow")
    st.subheader("Novo Lançamento")
    
    with st.form("form_novo", clear_on_submit=True):
        n_nota = st.text_input("Número da Nota (PDV)")
        vendedor = st.text_input("Vendedor")
        categoria = st.selectbox("Categoria", ["Mudança de Endereço", "Agendamento", "Retirada", "Aviso"])
        obs = st.text_area("Observação")
        
        # Correção para o "Aguardando Ctrl+V"
        img_file = st.file_uploader("Anexar Print (ou arraste aqui)", type=['png', 'jpg'])
        
        if st.form_submit_button("Lançar Pedido", use_container_width=True):
            if n_nota:
                blob = img_file.read() if img_file else None
                conn.cursor().execute(
                    "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, obs, categoria, data_hora) VALUES (?,?,?,?,?)",
                    (n_nota, vendedor, obs, categoria, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()
                st.success(f"Nota {n_nota} inserida!")
                st.rerun()

# --- PAINEL PRINCIPAL (GRID DE DADOS) ---
st.title("Controle de Expedição")
st.caption("Gerencie seus pedidos de forma eficiente")

# Barra de Busca
busca = st.text_input("🔍 Pesquisar por PDV...", placeholder="Digite o número da nota")

# Leitura dos Dados
df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY data_hora DESC", conn)

if busca:
    df = df[df['id_nota'].str.contains(busca)]

if not df.empty:
    # Cabeçalho da Tabela (Estilo Data Grid)
    c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1.5, 1.5, 0.8, 1])
    c1.markdown("**PDV**")
    c2.markdown("**VENDEDOR**")
    c3.markdown("**STATUS**")
    c4.markdown("**CATEGORIA**")
    c5.markdown("**ANEXO**")
    c6.markdown("**AÇÕES**")
    st.divider()

    for index, row in df.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1.5, 1.5, 0.8, 1])
        
        col1.write(f"**{row['id_nota']}**")
        col2.write(row['vendedor'])
        
        # Status Badge
        s_class = "status-inserido" if row['status'] == 'Inserido' else "status-finalizado"
        col3.markdown(f'<span class="status-badge {s_class}">{row["status"]}<br><small>{row["data_hora"]}</small></span>', unsafe_allow_html=True)
        
        # Categoria
        col4.markdown(f'<span class="cat-tag">{row["categoria"]}</span>', unsafe_allow_html=True)
        
        # Visualizar Imagem
        if row['anexo']:
            if col5.button("👁️", key=f"v_{row['id_nota']}"):
                st.image(row['anexo'], caption=f"Print da Nota {row['id_nota']}")
        else:
            col5.write("-")
            
        # Ações (Botões estilo "Produzir/Finalizar" da imagem)
        if row['status'] == 'Inserido':
            if col6.button("✅ Finalizar", key=f"f_{row['id_nota']}", use_container_width=True):
                conn.cursor().execute("UPDATE pedidos SET status = 'Finalizado' WHERE id_nota = ?", (row['id_nota'],))
                conn.commit()
                st.rerun()
        else:
            if col6.button("🗑️ Excluir", key=f"d_{row['id_nota']}", use_container_width=True):
                conn.cursor().execute("DELETE FROM pedidos WHERE id_nota = ?", (row['id_nota'],))
                conn.commit()
                st.rerun()
else:
    st.info("Nenhuma nota encontrada no sistema.")
