import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="📑")

# --- 2. BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
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

# --- 3. CSS PARA REPLICAR O LAYOUT "MARCOS GESTÕES" ---
st.markdown("""
    <style>
    /* Estilo do Fundo e Container */
    .stApp { background-color: #F4F7F6 !important; }
    
    /* Menu Lateral */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E0E0E0;
    }
    
    /* Estilização da Tabela */
    .main-table {
        width: 100%;
        background-color: white;
        border-radius: 10px;
        border-collapse: collapse;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .main-table th {
        background-color: #F8F9FA;
        color: #707070;
        text-align: left;
        padding: 15px;
        border-bottom: 2px solid #F1F1F1;
        font-size: 13px;
        text-transform: uppercase;
    }
    .main-table td {
        padding: 15px;
        border-bottom: 1px solid #F1F1F1;
        color: #333;
        font-size: 14px;
    }

    /* Status Tags (Inspirado na imagem) */
    .status-badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
    }
    .status-inserido { background-color: #E3F2FD; color: #1976D2; }
    .status-produzindo { background-color: #FFF9C4; color: #FBC02D; }
    .status-concluido { background-color: #E8F5E9; color: #2E7D32; }

    /* Categoria Tags */
    .cat-badge {
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
        background-color: #F1F1F1;
        color: #666;
    }

    /* Botões de Ação */
    .btn-action {
        padding: 6px 12px;
        border-radius: 5px;
        text-decoration: none;
        font-size: 12px;
        font-weight: bold;
        margin-right: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BARRA LATERAL (MENU) ---
with st.sidebar:
    st.title("📦 ExpedFlow")
    menu = st.radio("Navegação", ["Dashboard", "Todos os Pedidos", "Administração"], label_visibility="collapsed")
    
    st.divider()
    st.subheader("➕ Novo Lançamento")
    with st.form("novo_pedido", clear_on_submit=True):
        nota = st.text_input("Número da Nota (PDV)")
        vendedor = st.text_input("Vendedor")
        categoria = st.selectbox("Categoria", ["Mudança de Endereço", "Agendamento", "Retirada na Indústria", "Aviso Geral"])
        obs = st.text_area("Observação")
        
        # Receptor de imagem (Ctrl+V ou Arquivo)
        img_file = st.file_uploader("Anexar Print", type=['png', 'jpg'])
        
        if st.form_submit_button("Lançar Pedido", use_container_width=True):
            if nota:
                blob = img_file.read() if img_file else None
                conn.cursor().execute(
                    "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, obs, categoria, data_hora) VALUES (?,?,?,?,?)",
                    (nota, vendedor, obs, categoria, datetime.now())
                )
                conn.commit()
                st.success("Pedido Inserido!")
                st.rerun()

# --- 5. PAINEL PRINCIPAL (LAYOUT DE TABELA) ---
st.header("Controle de Notas e Expedição")
st.caption("Gerencie as demandas de entrega e retiradas de forma eficiente")

# Filtros (estilo busca da imagem)
search_col, filter_col = st.columns([3, 1])
with search_col:
    busca = st.text_input("Pesquisar por PDV/Nota...", placeholder="Digite o número da nota...")

# Carregar dados
query = "SELECT * FROM pedidos ORDER BY data_hora DESC"
df = pd.read_sql_query(query, conn)

if busca:
    df = df[df['id_nota'].str.contains(busca)]

# Renderizar Tabela Estilizada
if not df.empty:
    # Cabeçalho da Tabela
    cols = st.columns([1, 1, 1.5, 1.5, 1, 1])
    headers = ["PDV", "VENDEDOR", "STATUS", "CATEGORIA", "ANEXO", "AÇÕES"]
    for col, h in zip(cols, headers):
        col.markdown(f"**{h}**")
    
    st.divider()

    for i, row in df.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1.5, 1.5, 1, 1])
        
        c1.write(f"**{row['id_nota']}**")
        c2.write(row['vendedor'])
        
        # Badge de Status
        status_class = "status-inserido" if row['status'] == 'Inserido' else "status-concluido"
        c3.markdown(f'<span class="status-badge {status_class}">{row['status']}<br><small>{row['data_hora'][:16]}</small></span>', unsafe_allow_html=True)
        
        # Badge de Categoria
        c4.markdown(f'<span class="cat-badge">{row['categoria']}</span>', unsafe_allow_html=True)
        
        # Anexo
        if row['anexo']:
            c5.button("👁️ Ver", key=f"img_{row['id_nota']}")
        else:
            c5.write("-")
        
        # Botões de Ação
        if row['status'] == 'Inserido':
            if c6.button("✅ Concluir", key=f"done_{row['id_nota']}"):
                conn.cursor().execute("UPDATE pedidos SET status = 'Finalizado' WHERE id_nota = ?", (row['id_nota'],))
                conn.commit()
                st.rerun()
        else:
            if c6.button("🗑️ Excluir", key=f"del_{row['id_nota']}"):
                conn.cursor().execute("DELETE FROM pedidos WHERE id_nota = ?", (row['id_nota'],))
                conn.commit()
                st.rerun()
else:
    st.info("Nenhum pedido encontrado.")
