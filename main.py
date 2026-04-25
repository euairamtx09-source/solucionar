import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64

# --- 1. CONFIGURAÇÃO DE AMBIENTE PRO ---
st.set_page_config(layout="wide", page_title="ExpedFlow | Gestão de Notas", page_icon="📑")

# --- 2. MOTOR DE BANCO DE DADOS (ANTI-CRASH) ---
def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
    # Criamos a estrutura com integridade de dados
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
    # Auto-reparo de colunas (Caso o banco seja antigo)
    colunas = [('obs', 'TEXT'), ('categoria', 'TEXT'), ('anexo', 'BLOB'), ('data_hora', 'TEXT')]
    for col, tipo in colunas:
        try: cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {col} {tipo}")
        except: pass
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. CSS CUSTOMIZADO (ALTO PADRÃO) ---
st.markdown("""
    <style>
    /* Reset de Cores para Leitura Nítida */
    .stApp { background-color: #F4F7F9 !important; }
    h1, h2, h3, p, span, label, th, td { color: #1E293B !important; font-family: 'Inter', sans-serif; }
    
    /* Barra Lateral Estilo Dashboard */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
        width: 380px !important;
    }
    
    /* Estilização da Tabela de Dados (Grid) */
    .data-row {
        background-color: #FFFFFF;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
    }

    /* Status Badges Profissionais */
    .badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-inserido { background-color: #DBEAFE; color: #1E40AF; border: 1px solid #BFDBFE; }
    .status-concluido { background-color: #DCFCE7; color: #166534; border: 1px solid #BBF7D0; }

    /* Tags de Categoria */
    .tag-cat {
        background-color: #F1F5F9;
        color: #475569;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        border: 1px solid #CBD5E1;
    }

    /* Botão de Ação Estilizado */
    .stButton>button {
        border-radius: 6px;
        border: 1px solid #CBD5E1;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        border-color: #1E40AF;
        color: #1E40AF;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BARRA LATERAL: INPUT DE DADOS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2343/2343894.png", width=50)
    st.title("Gestão de Notas")
    
    st.subheader("📥 Novo Lançamento")
    with st.form("form_registro", clear_on_submit=True):
        f_nota = st.text_input("Nota Fiscal / PDV", placeholder="Ex: 45990")
        f_vend = st.text_input("Vendedor")
        f_cat = st.selectbox("Categoria", [
            "Mudança de Endereço", 
            "Agendamento de Entrega", 
            "Retirada na Indústria", 
            "Aviso Geral"
        ])
        f_obs = st.text_area("Observação / Instrução")
        f_img = st.file_uploader("Anexar Print da Nota", type=['png', 'jpg', 'jpeg'])
        
        if st.form_submit_button("REGISTRAR NOTA", use_container_width=True):
            if f_nota and f_vend:
                img_blob = f_img.read() if f_img else None
                data_agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                db_conn.cursor().execute(
                    "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, obs, categoria, anexo, data_hora) VALUES (?,?,?,?,?,?)",
                    (f_nota, f_vend, f_obs, f_cat, img_blob, data_agora)
                )
                db_conn.commit()
                st.success(f"Nota {f_nota} registrada!")
                st.rerun()
            else:
                st.error("Preencha Nota e Vendedor.")

# --- 5. PAINEL PRINCIPAL: DATA GRID ---
st.title("📋 Painel de Controle de Expedição")
st.markdown("---")

# Filtros de Pesquisa Rápida
c_busca, c_filtro, _ = st.columns([2, 1, 1])
with c_busca:
    query_search = st.text_input("🔍 Localizar por Nota ou Vendedor...", placeholder="Digite para filtrar...")

# Carregamento dos Dados via Pandas
try:
    df_db = pd.read_sql_query("SELECT * FROM pedidos ORDER BY data_hora DESC", db_conn)
except:
    df_db = pd.DataFrame(columns=['id_nota', 'vendedor', 'obs', 'categoria', 'status', 'anexo', 'data_hora'])

# Aplicação do Filtro
if query_search:
    df = df_db[df_db['id_nota'].str.contains(query_search) | df_db['vendedor'].str.contains(query_search, case=False)]
else:
    df = df_db

# CABEÇALHO DO GRID
h = st.columns([1, 1.2, 1.5, 1.5, 0.8, 1])
h[0].markdown("**PDV/NOTA**")
h[1].markdown("**VENDEDOR**")
h[2].markdown("**STATUS / DATA**")
h[3].markdown("**CATEGORIA**")
h[4].markdown("**ANEXO**")
h[5].markdown("**AÇÕES**")
st.markdown("<div style='margin-top:-15px'>---</div>", unsafe_allow_html=True)

# LINHAS DO GRID
if df.empty:
    st.info("Nenhuma nota encontrada.")
else:
    for i, row in df.iterrows():
        r = st.columns([1, 1.2, 1.5, 1.5, 0.8, 1])
        
        # PDV e Vendedor
        r[0].write(f"**{row['id_nota']}**")
        r[1].write(row['vendedor'])
        
        # Status e Data
        s_class = "status-inserido" if row['status'] == 'Inserido' else "status-concluido"
        r[2].markdown(f'<span class="badge {s_class}">{row["status"]}</span><br><small>{row["data_hora"]}</small>', unsafe_allow_html=True)
        
        # Categoria e Observação
        obs_curta = (row['obs'][:30] + '...') if row['obs'] and len(row['obs']) > 30 else (row['obs'] or "")
        r[3].markdown(f'<span class="tag-cat">{row["categoria"]}</span><br><small>{obs_curta}</small>', unsafe_allow_html=True)
        
        # Visualização de Anexo (Botão Ícone)
        if row['anexo']:
            if r[4].button("👁️ Ver", key=f"v_{row['id_nota']}"):
                st.image(row['anexo'], caption=f"Anexo da Nota {row['id_nota']}", use_container_width=False, width=400)
        else:
            r[4].write("-")
            
        # Ações Diretas
        if row['status'] == 'Inserido':
            if r[5].button("✅ Concluir", key=f"c_{row['id_nota']}", use_container_width=True):
                db_conn.cursor().execute("UPDATE pedidos SET status = 'Concluído' WHERE id_nota = ?", (row['id_nota'],))
                db_conn.commit()
                st.rerun()
        else:
            if r[5].button("🗑️ Excluir", key=f"d_{row['id_nota']}", use_container_width=True):
                db_conn.cursor().execute("DELETE FROM pedidos WHERE id_nota = ?", (row['id_nota'],))
                db_conn.commit()
                st.rerun()

# --- 6. RODAPÉ ---
st.markdown("---")
st.caption(f"ExpedFlow Pro | Sistema Conectado | {len(df)} registros exibidos")
