import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="📑")

# --- 2. MOTOR DE BANCO DE DADOS (COM TRATAMENTO DE ERRO) ---
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
            data_hora TEXT
        )
    ''')
    # Garante que colunas novas existam para evitar KeyError
    colunas = [('obs', 'TEXT'), ('categoria', 'TEXT'), ('anexo', 'BLOB'), ('data_hora', 'TEXT')]
    for col, tipo in colunas:
        try: cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {col} {tipo}")
        except: pass
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. CSS DE ALTO CONTRASTE (PARA NÃO APAGAR NO BRANCO) ---
st.markdown("""
    <style>
    /* Bloqueio de Tema: Fundo Cinza Azulado para dar contraste */
    .stApp { 
        background-color: #F0F2F5 !important; 
    }

    /* FORÇA TEXTO PRETO EM TUDO: Inputs, Títulos, Labels e Tabelas */
    h1, h2, h3, p, span, label, th, td, .stMarkdown, .stTextInput label { 
        color: #1A1A1B !important; 
        font-weight: 700 !important;
        opacity: 1 !important;
    }

    /* Barra Lateral Sólida */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 2px solid #CED4DA;
    }

    /* Cabeçalho da Tabela (Fundo Escuro, Texto Branco para destacar) */
    .table-header {
        background-color: #343A40;
        padding: 12px;
        border-radius: 8px 8px 0px 0px;
        display: flex;
        justify-content: space-between;
    }
    .header-item {
        color: #FFFFFF !important;
        font-size: 12px;
        text-transform: uppercase;
        font-weight: 800;
    }

    /* Linha da Tabela (Estilo Grid Profissional) */
    .grid-row {
        background-color: #FFFFFF;
        padding: 15px;
        border: 1px solid #DEE2E6;
        border-top: none;
        display: flex;
        align-items: center;
        transition: 0.2s;
    }
    .grid-row:hover { background-color: #F8F9FA; }

    /* Tags de Status Visíveis */
    .status-tag {
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        border: 1px solid #000;
    }
    .status-blue { background-color: #CFE2FF; color: #084298 !important; }
    .status-green { background-color: #D1E7DD; color: #0F5132 !important; }

    /* Botões */
    .stButton>button {
        border: 1px solid #000 !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BARRA LATERAL (CADASTRO) ---
with st.sidebar:
    st.markdown("## 📥 Novo Registro")
    
    with st.form("form_registro", clear_on_submit=True):
        f_nota = st.text_input("NÚMERO DA NOTA (PDV)")
        f_vend = st.text_input("VENDEDOR")
        f_cat = st.selectbox("CATEGORIA", [
            "Mudança de Endereço", 
            "Agendamento de Entrega", 
            "Retirada na Indústria", 
            "Aviso Geral"
        ])
        f_obs = st.text_area("OBSERVAÇÕES")
        f_img = st.file_uploader("ANEXAR PRINT", type=['png', 'jpg', 'jpeg'])
        
        if st.form_submit_button("LANÇAR NOTA", use_container_width=True):
            if f_nota and f_vend:
                img_blob = f_img.read() if f_img else None
                data_str = datetime.now().strftime("%d/%m/%Y %H:%M")
                db_conn.cursor().execute(
                    "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, obs, categoria, anexo, data_hora) VALUES (?,?,?,?,?,?)",
                    (f_nota, f_vend, f_obs, f_cat, img_blob, data_str)
                )
                db_conn.commit()
                st.rerun()

# --- 5. PAINEL DE CONTROLE (DATA GRID) ---
st.title("📑 Gestão de Expedição")

# Busca
search = st.text_input("🔍 PESQUISAR NOTA...", placeholder="Digite o número...")

# Dados
df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY data_hora DESC", db_conn)
if search:
    df = df[df['id_nota'].str.contains(search) | df['vendedor'].str.contains(search, case=False)]

# Cabeçalho do Grid
st.markdown("""
    <div class="table-header">
        <div style="width: 15%;" class="header-item">Nota</div>
        <div style="width: 20%;" class="header-item">Vendedor</div>
        <div style="width: 20%;" class="header-item">Status / Data</div>
        <div style="width: 25%;" class="header-item">Categoria / Obs</div>
        <div style="width: 10%;" class="header-item">Anexo</div>
        <div style="width: 10%;" class="header-item">Ação</div>
    </div>
    """, unsafe_allow_html=True)

# Linhas
if df.empty:
    st.warning("Nenhum registro encontrado.")
else:
    for i, row in df.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([0.15, 0.20, 0.20, 0.25, 0.10, 0.10])
        
        with st.container():
            c1.markdown(f"**{row['id_nota']}**")
            c2.write(row['vendedor'])
            
            # Status
            s_color = "status-blue" if row['status'] == 'Inserido' else "status-green"
            c3.markdown(f'<span class="status-tag {s_color}">{row["status"]}</span>', unsafe_allow_html=True)
            c3.markdown(f'<small style="color: #666;">{row["data_hora"]}</small>', unsafe_allow_html=True)
            
            # Categoria
            c4.markdown(f"**{row['categoria']}**")
            c4.markdown(f"<small>{row['obs'][:30]}...</small>", unsafe_allow_html=True)
            
            # Imagem
            if row['anexo']:
                if c5.button("👁️", key=f"img_{row['id_nota']}"):
                    st.image(row['anexo'], width=400)
            else: c5.write("-")
            
            # Ações
            if row['status'] == 'Inserido':
                if c6.button("✅", key=f"ok_{row['id_nota']}"):
                    db_conn.cursor().execute("UPDATE pedidos SET status = 'Finalizado' WHERE id_nota = ?", (row['id_nota'],))
                    db_conn.commit()
                    st.rerun()
            else:
                if c6.button("🗑️", key=f"del_{row['id_nota']}"):
                    db_conn.cursor().execute("DELETE FROM pedidos WHERE id_nota = ?", (row['id_nota'],))
                    db_conn.commit()
                    st.rerun()
        st.markdown("<div style='border-bottom: 1px solid #DDD;'></div>", unsafe_allow_html=True)
