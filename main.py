import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64

# --- 1. CONFIGURAÇÃO DE PÁGINA (MODERNA) ---
st.set_page_config(layout="wide", page_title="ExpedFlow Elite", page_icon="🏢")

# --- 2. BANCO DE DADOS (BLINDADO) ---
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
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. CSS "DESIGN SYSTEM" (O FIM DO VISUAL FEIO) ---
st.markdown("""
    <style>
    /* Importação de fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }

    /* Fundo suave para destacar os elementos brancos */
    .stApp { background-color: #F8FAFC !important; }
    
    /* Barra Lateral - Visual de Aplicativo */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
        padding-top: 2rem;
    }

    /* Cabeçalho de Tabela Customizado */
    .table-header {
        background-color: #F1F5F9;
        padding: 15px;
        border-radius: 8px 8px 0px 0px;
        border: 1px solid #E2E8F0;
        margin-bottom: -1px;
    }
    .header-text {
        color: #64748B !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Linha de Dados (Data Grid) */
    .data-row {
        background-color: #FFFFFF;
        padding: 20px;
        border: 1px solid #E2E8F0;
        border-top: none;
        transition: background-color 0.2s;
        display: flex;
        align-items: center;
    }
    .data-row:hover { background-color: #F8FAFC; }
    .data-row:last-child { border-radius: 0px 0px 8px 8px; }

    /* Estilização de Badges e Tags */
    .status-pill {
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 600;
        border: 1px solid transparent;
    }
    .pill-inserido { background-color: #EFF6FF; color: #1D4ED8; border-color: #DBEAFE; }
    .pill-concluido { background-color: #F0FDF4; color: #15803D; border-color: #DCFCE7; }

    .cat-tag {
        color: #475569;
        font-size: 13px;
        font-weight: 600;
    }

    /* Inputs e Botões Limpos */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
    }
    
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: 1px solid #E2E8F0 !important;
        background-color: white !important;
        color: #1E293B !important;
    }
    .stButton>button:hover {
        border-color: #3B82F6 !important;
        color: #3B82F6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BARRA LATERAL (CADASTRO LIMPO) ---
with st.sidebar:
    st.markdown("<h2 style='color:#1E293B; margin-bottom:20px;'>ExpedFlow Pro</h2>", unsafe_allow_html=True)
    
    with st.form("form_clean", clear_on_submit=True):
        st.markdown("**📝 Informações da Nota**")
        f_nota = st.text_input("PDV / Nota Fiscal", placeholder="Ex: 50400")
        f_vend = st.text_input("Responsável (Vendedor)")
        
        st.markdown("**📂 Classificação**")
        f_cat = st.selectbox("Categoria", [
            "Mudança de Endereço", 
            "Agendamento de Entrega", 
            "Retirada na Indústria", 
            "Aviso Geral"
        ])
        f_obs = st.text_area("Observações Técnicas", placeholder="Descreva os detalhes aqui...")
        f_img = st.file_uploader("Anexar Comprovante/Print", type=['png', 'jpg'])
        
        if st.form_submit_button("REGISTRAR NO SISTEMA", use_container_width=True):
            if f_nota and f_vend:
                img_blob = f_img.read() if f_img else None
                data_iso = datetime.now().strftime("%d/%m/%Y %H:%M")
                db_conn.cursor().execute(
                    "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, obs, categoria, anexo, data_hora) VALUES (?,?,?,?,?,?)",
                    (f_nota, f_vend, f_obs, f_cat, img_blob, data_iso)
                )
                db_conn.commit()
                st.toast(f"Nota {f_nota} salva com sucesso!", icon="✅")
                st.rerun()

# --- 5. PAINEL PRINCIPAL (GRID ESTILO SaaS) ---
st.markdown("<h1 style='color:#0F172A; font-size: 1.8rem;'>Controle de Notas e Expedição</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B;'>Gerencie e monitore o fluxo de saída em tempo real.</p>", unsafe_allow_html=True)

# Área de Pesquisa
c_search, _ = st.columns([2, 2])
with c_search:
    busca = st.text_input("🔍 Buscar por PDV ou Vendedor", placeholder="Digite para filtrar a lista...")

# Dados
try:
    df_full = pd.read_sql_query("SELECT * FROM pedidos ORDER BY data_hora DESC", db_conn)
except:
    df_full = pd.DataFrame(columns=['id_nota', 'vendedor', 'obs', 'categoria', 'status', 'anexo', 'data_hora'])

if busca:
    df = df_full[df_full['id_nota'].str.contains(busca) | df_full['vendedor'].str.contains(busca, case=False)]
else:
    df = df_full

# ESTRUTURA DO GRID (CABECALHO)
st.markdown("""
    <div class="table-header">
        <div style="display: flex; justify-content: space-between;">
            <div style="width: 15%;" class="header-text">PDV / Nota</div>
            <div style="width: 20%;" class="header-text">Vendedor</div>
            <div style="width: 20%;" class="header-text">Status / Data</div>
            <div style="width: 25%;" class="header-text">Categoria / Detalhes</div>
            <div style="width: 10%;" class="header-text">Arquivo</div>
            <div style="width: 10%;" class="header-text">Ações</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# LINHAS DO GRID
if df.empty:
    st.info("Nenhum registro encontrado.")
else:
    for i, row in df.iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([0.15, 0.20, 0.20, 0.25, 0.10, 0.10])
        
        with st.container():
            c1.markdown(f"<p style='font-weight:700; color:#1E293B;'>#{row['id_nota']}</p>", unsafe_allow_html=True)
            c2.markdown(f"<p style='color:#475569;'>{row['vendedor']}</p>", unsafe_allow_html=True)
            
            # Badge Status
            s_pill = "pill-inserido" if row['status'] == 'Inserido' else "pill-concluido"
            c3.markdown(f'<span class="status-pill {s_pill}">{row["status"]}</span>', unsafe_allow_html=True)
            c3.markdown(f'<p style="font-size:11px; color:#94A3B8; margin-top:4px;">{row["data_hora"]}</p>', unsafe_allow_html=True)
            
            # Categoria
            c4.markdown(f'<span class="cat-tag">{row["categoria"]}</span>', unsafe_allow_html=True)
            c4.markdown(f'<p style="font-size:12px; color:#64748B;">{row["obs"][:40]}...</p>', unsafe_allow_html=True)
            
            # Anexo
            if row['anexo']:
                if c5.button("👁️", key=f"v_{row['id_nota']}"):
                    st.image(row['anexo'], width=350)
            else:
                c5.write("-")
            
            # Ações
            if row['status'] == 'Inserido':
                if c6.button("✅", key=f"c_{row['id_nota']}"):
                    db_conn.cursor().execute("UPDATE pedidos SET status = 'Concluído' WHERE id_nota = ?", (row['id_nota'],))
                    db_conn.commit()
                    st.rerun()
            else:
                if c6.button("🗑️", key=f"d_{row['id_nota']}"):
                    db_conn.cursor().execute("DELETE FROM pedidos WHERE id_nota = ?", (row['id_nota'],))
                    db_conn.commit()
                    st.rerun()
        st.markdown("<hr style='margin:0; border:0.5px solid #E2E8F0;'>", unsafe_allow_html=True)
