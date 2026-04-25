import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="🚚")

# --- 2. BANCO DE DADOS (Atualizado para Categorias) ---
def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id_nota TEXT PRIMARY KEY,
            vendedor TEXT,
            endereco TEXT,
            categoria TEXT,
            status TEXT DEFAULT 'PENDENTE',
            anexo BLOB,
            ultima_atualizacao DATETIME
        )
    ''')
    # Atualização de segurança para colunas novas
    try: cursor.execute("ALTER TABLE pedidos ADD COLUMN categoria TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE pedidos ADD COLUMN anexo BLOB")
    except: pass
    conn.commit()
    return conn

conn = init_db()

# --- 3. CSS DE ALTO CONTRASTE E CORES POR CATEGORIA ---
st.markdown("""
    <style>
    .stApp { background-color: #E5E7EB !important; }
    h1, h2, h3, p, span, label { color: #000000 !important; font-weight: 800 !important; }
    
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 3px solid #000000;
        width: 400px !important;
    }

    /* Estilização dos Cards baseada em Categorias */
    .card {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 10px;
        border: 3px solid #000000;
        margin-bottom: 15px;
        box-shadow: 5px 5px 0px #000000;
    }
    
    .cat-mudanca { border-left: 20px solid #DC2626 !important; } /* Vermelho */
    .cat-agendamento { border-left: 20px solid #2563EB !important; } /* Azul */
    .cat-retirada { border-left: 20px solid #D97706 !important; } /* Laranja */
    .cat-aviso { border-left: 20px solid #6B7280 !important; } /* Cinza */

    .tag {
        padding: 4px 10px;
        border-radius: 5px;
        color: white !important;
        font-size: 12px;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. JAVASCRIPT PARA CTRL+V ---
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

# --- 5. INTERFACE ---
st.title("🚚 ExpedFlow: Painel Categorizado")

with st.sidebar:
    st.header("📥 Lançar Nova Demanda")
    
    # Receptor de Imagem
    arquivo_upload = st.file_uploader("Arrastar Print", type=['png', 'jpg', 'jpeg'])
    buffer_colagem = st.text_input("Receptor Ctrl+V", placeholder="Clique e dê Ctrl+V", key="receptor")
    
    final_blob = None
    if arquivo_upload: final_blob = arquivo_upload.read()
    elif "data:image" in buffer_colagem:
        final_blob = base64.b64decode(buffer_colagem.split(",")[1])
        st.success("✅ Print capturado!")

    st.divider()

    with st.form("cadastro", clear_on_submit=True):
        n = st.text_input("Número da Nota")
        v = st.text_input("Vendedor")
        
        # O PONTO CHAVE: SELEÇÃO DE CATEGORIA
        cat = st.selectbox("Tipo de Demanda", [
            "Mudança de Endereço", 
            "Agendamento de Entrega", 
            "Retirada de Material", 
            "Aviso Geral"
        ])
        
        e = st.text_area("Detalhes/Observações")
        
        if st.form_submit_button("LANÇAR NOTA NO PAINEL"):
            if n:
                conn.cursor().execute(
                    "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, endereco, categoria, anexo, ultima_atualizacao) VALUES (?,?,?,?,?,?)",
                    (n, v, e, cat, final_blob, datetime.now())
                )
                conn.commit()
                st.rerun()

# --- 6. PAINEL DE EXIBIÇÃO ---
df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY ultima_atualizacao DESC", conn)
col_mesa, col_patio = st.columns([2, 1])

with col_mesa:
    st.subheader("📋 Fila de Notas (Infinito)")
    pendentes = df[df['status'] == 'PENDENTE']
    
    for _, row in pendentes.iterrows():
        # Define a classe CSS baseada na categoria
        css_cat = "cat-aviso"
        cor_tag = "#6B7280"
        
        if row['categoria'] == "Mudança de Endereço":
            css_cat, cor_tag = "cat-mudanca", "#DC2626"
        elif row['categoria'] == "Agendamento de Entrega":
            css_cat, cor_tag = "cat-agendamento", "#2563EB"
        elif row['categoria'] == "Retirada de Material":
            css_cat, cor_tag = "cat-retirada", "#D97706"

        with st.container():
            st.markdown(f"""
                <div class="card {css_cat}">
                    <span class="tag" style="background-color: {cor_tag};">{row['categoria']}</span>
                    <p style="margin-top:10px; font-size:14px;">Vendedor: {row['vendedor']}</p>
                    <h2 style="margin:0;">Nota #{row['id_nota']}</h2>
                    <p style="font-size:18px; margin-top:10px; background:#f9f9f9; padding:10px; border-radius:5px;">{row['endereco']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if row['anexo']:
                with st.expander("🖼️ Ver Print"):
                    st.image(row['anexo'])
            
            if st.button(f"CONCLUIR NOTA {row['id_nota']}", key=f"btn_{row['id_nota']}"):
                conn.cursor().execute("UPDATE pedidos SET status = 'CONCLUIDO' WHERE id_nota = ?", (row['id_nota'],))
                conn.commit()
                st.rerun()

with col_patio:
    st.subheader("✅ Histórico (Hoje)")
    concluidos = df[df['status'] == 'CONCLUIDO']
    st.dataframe(concluidos[['id_nota', 'vendedor', 'categoria']], use_container_width=True)
