import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="📑")

# --- 2. BANCO DE DADOS (Auto-Reparo de Colunas) ---
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
    # Força a existência de colunas para evitar erros de 'KeyError'
    for col, tipo in [('obs','TEXT'), ('categoria','TEXT'), ('anexo','BLOB'), ('data_hora','TEXT')]:
        try: cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {col} {tipo}")
        except: pass
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. CSS "ULTRA-CONTRASTE" (RESOLVE O TEXTO QUE APAGA) ---
st.markdown("""
    <style>
    /* Fundo da página em cinza industrial para destacar as tabelas */
    .stApp { background-color: #E2E8F0 !important; }

    /* FORÇA O TEXTO A SER PRETO EM TUDO */
    h1, h2, h3, p, span, label, td, th, .stMarkdown { 
        color: #000000 !important; 
        font-weight: 700 !important; 
    }

    /* Barra Lateral Estilo Painel de Controle */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 3px solid #1E293B;
    }

    /* Estilização da Tabela (Data Grid) */
    .table-container {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 2px solid #1E293B;
        overflow: hidden;
    }

    .custom-header {
        background-color: #1E293B; /* Azul Escuro/Preto */
        padding: 15px;
        display: flex;
        justify-content: space-between;
        border-bottom: 2px solid #000000;
    }

    .header-col {
        color: #FFFFFF !important; /* Texto Branco no Fundo Escuro */
        font-size: 13px;
        font-weight: 800;
        text-transform: uppercase;
    }

    /* Linhas da Tabela */
    .grid-row {
        background-color: #FFFFFF;
        border-bottom: 1px solid #CBD5E1;
        padding: 12px 15px;
        display: flex;
        align-items: center;
    }

    /* Tags Coloridas (Sem transparência para não sumir) */
    .tag {
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 12px;
        border: 1px solid #000000;
    }
    .tag-blue { background-color: #3B82F6; color: #FFFFFF !important; }
    .tag-green { background-color: #22C55E; color: #FFFFFF !important; }
    .tag-cat { background-color: #F1F5F9; color: #000000 !important; border: 1px solid #94A3B8; }

    /* Botões Grandes e Sólidos */
    .stButton>button {
        border: 2px solid #000000 !important;
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 800 !important;
    }
    .stButton>button:hover {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.markdown("### 📥 LANÇAMENTO")
    with st.form("registro_pro", clear_on_submit=True):
        f_nota = st.text_input("NOTA / PDV")
        f_vend = st.text_input("VENDEDOR")
        f_cat = st.selectbox("CATEGORIA", ["Mudança de Endereço", "Agendamento", "Retirada", "Aviso"])
        f_obs = st.text_area("OBSERVAÇÕES")
        f_img = st.file_uploader("PRINT DA NOTA", type=['png', 'jpg'])
        
        if st.form_submit_button("CADASTRAR", use_container_width=True):
            if f_nota:
                blob = f_img.read() if f_img else None
                data_h = datetime.now().strftime("%d/%m %H:%M")
                db_conn.cursor().execute(
                    "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, obs, categoria, anexo, data_hora) VALUES (?,?,?,?,?,?)",
                    (f_nota, f_vend, f_obs, f_cat, blob, data_h)
                )
                db_conn.commit()
                st.rerun()

# --- 5. PAINEL PRINCIPAL (GRID PROFISSIONAL) ---
st.title("📑 CONTROLE DE EXPEDIÇÃO")

# Busca Simples
busca = st.text_input("🔎 BUSCAR NOTA OU VENDEDOR...")

# Dados
df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY data_hora DESC", db_conn)
if busca:
    df = df[df['id_nota'].str.contains(busca) | df['vendedor'].str.contains(busca, case=False)]

# Cabeçalho Fixo
st.markdown("""
    <div class="custom-header">
        <div style="width: 10%;" class="header-col">Nota</div>
        <div style="width: 15%;" class="header-col">Vendedor</div>
        <div style="width: 15%;" class="header-col">Status</div>
        <div style="width: 35%;" class="header-col">Categoria / Detalhes</div>
        <div style="width: 10%;" class="header-col">Print</div>
        <div style="width: 15%;" class="header-col">Ação</div>
    </div>
    """, unsafe_allow_html=True)

# Linhas de Dados
if df.empty:
    st.info("Fila vazia.")
else:
    for i, row in df.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([0.1, 0.15, 0.15, 0.35, 0.1, 0.15])
        
        with st.container():
            c1.markdown(f"**{row['id_nota']}**")
            c2.write(row['vendedor'])
            
            # Status Badge
            s_tag = "tag-blue" if row['status'] == 'Inserido' else "tag-green"
            c3.markdown(f'<span class="tag {s_tag}">{row["status"]}</span>', unsafe_allow_html=True)
            c3.markdown(f'<small>{row["data_hora"]}</small>', unsafe_allow_html=True)
            
            # Categoria / Obs
            c4.markdown(f'<span class="tag tag-cat">{row["categoria"]}</span>', unsafe_allow_html=True)
            c4.markdown(f'<p style="font-size:12px; margin-top:5px;">{row["obs"]}</p>', unsafe_allow_html=True)
            
            # Print
            if row['anexo']:
                if c5.button("👁️", key=f"img_{row['id_nota']}"):
                    st.image(row['anexo'], width=500)
            else: c5.write("-")
            
            # Ações
            if row['status'] == 'Inserido':
                if c6.button("✅ CONCLUIR", key=f"f_{row['id_nota']}", use_container_width=True):
                    db_conn.cursor().execute("UPDATE pedidos SET status = 'Finalizado' WHERE id_nota = ?", (row['id_nota'],))
                    db_conn.commit()
                    st.rerun()
            else:
                if c6.button("🗑️ APAGAR", key=f"d_{row['id_nota']}", use_container_width=True):
                    db_conn.cursor().execute("DELETE FROM pedidos WHERE id_nota = ?", (row['id_nota'],))
                    db_conn.commit()
                    st.rerun()
        st.markdown("<hr style='margin:0; border-top: 1px solid #94A3B8;'>", unsafe_allow_html=True)
