import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="📑")

# --- 2. BANCO DE DADOS (Auto-Reparável contra Erros de Coluna) ---
def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
    # Cria a tabela se não existir
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
    # Prevenção de KeyError/DatabaseError: Garante que as colunas existam
    colunas_necessarias = [
        ('obs', 'TEXT'),
        ('categoria', 'TEXT'),
        ('anexo', 'BLOB'),
        ('data_hora', 'DATETIME')
    ]
    for col_nome, col_tipo in colunas_necessarias:
        try:
            cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {col_nome} {col_tipo}")
        except:
            pass # Coluna já existe
    conn.commit()
    return conn

conn = init_db()

# --- 3. CSS PARA LAYOUT PROFISSIONAL (Estilo Marcos Gestões) ---
st.markdown("""
    <style>
    /* Estilo Geral */
    .stApp { background-color: #F8F9FA !important; }
    h1, h2, h3, p, span, label, th, td { color: #212529 !important; font-weight: 700 !important; }

    /* Menu Lateral Branco */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #DEE2E6;
        width: 400px !important;
    }

    /* Status Badges */
    .badge {
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: bold;
        display: inline-block;
        text-align: center;
    }
    .badge-inserido { background-color: #E3F2FD; color: #0D47A1 !important; border: 1px solid #0D47A1; }
    .badge-finalizado { background-color: #E8F5E9; color: #1B5E20 !important; border: 1px solid #1B5E20; }

    /* Tags de Categoria */
    .cat-tag {
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 4px;
        background-color: #E9ECEF;
        border: 1px solid #CED4DA;
    }

    /* Botões de Ação Compactos */
    .stButton>button {
        border-radius: 4px;
        font-weight: bold;
        height: 2.2em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SCRIPT PARA CAPTURA DE CTRL+V ---
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

# --- 5. BARRA LATERAL (ENTRADA DE DADOS) ---
with st.sidebar:
    st.title("📑 ExpedFlow")
    st.subheader("➕ Novo Lançamento")
    
    # Campo para Ctrl+V
    buffer_v = st.text_input("Status do Print:", placeholder="Clique e dê Ctrl+V", key="v_pasted")
    up_file = st.file_uploader("Ou arraste o arquivo", type=['png', 'jpg', 'jpeg'])
    
    img_blob = None
    if up_file:
        img_blob = up_file.read()
    elif "data:image" in buffer_v:
        img_blob = base64.b64decode(buffer_v.split(",")[1])
        st.success("✅ Print capturado via Colagem!")

    st.divider()

    with st.form("cadastro", clear_on_submit=True):
        f_nota = st.text_input("Número da Nota (PDV)")
        f_vend = st.text_input("Vendedor")
        f_cat = st.selectbox("Categoria da Demanda", [
            "Mudança de Endereço", 
            "Agendamento de Entrega", 
            "Retirada na Indústria", 
            "Aviso Geral"
        ])
        f_obs = st.text_area("Observação Técnica")
        
        if st.form_submit_button("LANÇAR NO SISTEMA", use_container_width=True):
            if f_nota:
                conn.cursor().execute(
                    "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, obs, categoria, anexo, data_hora) VALUES (?,?,?,?,?,?)",
                    (f_nota, f_vend, f_obs, f_cat, img_blob, datetime.now().strftime("%d/%m/%Y %H:%M"))
                )
                conn.commit()
                st.success(f"Nota {f_nota} lançada!")
                st.rerun()

# --- 6. PAINEL PRINCIPAL (DATA GRID PROFISSIONAL) ---
st.title("Controle de Produção e Notas")
st.caption("Gestão eficiente de expedição e logística interna")

# Busca e Filtros
col_search, col_spacer = st.columns([2, 2])
with col_search:
    search_query = st.text_input("🔍 Filtrar por nota ou vendedor...", placeholder="Ex: 154594")

# Carregamento Seguro dos Dados
try:
    df_raw = pd.read_sql_query("SELECT * FROM pedidos ORDER BY data_hora DESC", conn)
except:
    df_raw = pd.DataFrame(columns=['id_nota', 'vendedor', 'obs', 'categoria', 'status', 'anexo', 'data_hora'])

# Lógica de Busca
if search_query:
    df = df_raw[df_raw['id_nota'].str.contains(search_query) | df_raw['vendedor'].str.contains(search_query, case=False)]
else:
    df = df_raw

# Cabeçalho da Tabela
st.markdown("---")
h1, h2, h3, h4, h5, h6 = st.columns([1, 1, 1.2, 1.5, 0.6, 1])
h1.markdown("**PDV**")
h2.markdown("**VENDEDOR**")
h3.markdown("**STATUS**")
h4.markdown("**CATEGORIA**")
h5.markdown("**ARQ**")
h6.markdown("**AÇÕES**")
st.markdown("---")

if df.empty:
    st.info("Nenhuma nota aguardando na fila.")
else:
    for _, row in df.iterrows():
        r1, r2, r3, r4, r5, r6 = st.columns([1, 1, 1.2, 1.5, 0.6, 1])
        
        r1.write(f"**{row['id_nota']}**")
        r2.write(row['vendedor'])
        
        # Status Badge (Inspirado na Marcos Gestões)
        s_style = "badge-inserido" if row['status'] == 'Inserido' else "badge-finalizado"
        r3.markdown(f'<span class="badge {s_style}">{row["status"]}<br><small>{row["data_hora"]}</small></span>', unsafe_allow_html=True)
        
        # Categoria e Obs
        r4.markdown(f'<span class="cat-tag">{row["categoria"]}</span><br><small style="font-weight:normal;">{row["obs"][:40]}</small>', unsafe_allow_html=True)
        
        # Arquivo/Anexo
        if row['anexo']:
            if r5.button("👁️", key=f"img_{row['id_nota']}"):
                st.image(row['anexo'], caption=f"Print Nota {row['id_nota']}")
        else:
            r5.write("-")
        
        # Ações Dinâmicas
        if row['status'] == 'Inserido':
            if r6.button("✅ Finalizar", key=f"btn_f_{row['id_nota']}", use_container_width=True):
                conn.cursor().execute("UPDATE pedidos SET status = 'Finalizado' WHERE id_nota = ?", (row['id_nota'],))
                conn.commit()
                st.rerun()
        else:
            if r6.button("🗑️ Excluir", key=f"btn_d_{row['id_nota']}", use_container_width=True):
                conn.cursor().execute("DELETE FROM pedidos WHERE id_nota = ?", (row['id_nota'],))
                conn.commit()
                st.rerun()
