import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="🚚")

# --- 2. BANCO DE DADOS (Com Suporte a Anexos) ---
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
    # Garante que a coluna anexo exista em bancos antigos
    try:
        cursor.execute("ALTER TABLE pedidos ADD COLUMN anexo BLOB")
    except:
        pass
    conn.commit()
    return conn

conn = init_db()

# --- 3. MÁGICA DO CTRL+V E ESTILIZAÇÃO GOOGLE ---
st.markdown("""
    <script>
    // Script para capturar Ctrl+V globalmente na página
    const doc = window.parent.document;
    doc.addEventListener('paste', (event) => {
        const items = (event.clipboardData || event.originalEvent.clipboardData).items;
        for (const item of items) {
            if (item.kind === 'file') {
                const blob = item.getAsFile();
                const reader = new FileReader();
                reader.onload = function(e) {
                    const base64String = e.target.result;
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
    /* Fundo e Fontes - Alto Contraste Estilo Google */
    .stApp { background-color: #F8F9FA !important; }
    h1, h2, h3, p, span, label { color: #202124 !important; font-weight: 700 !important; }
    
    /* Barra Lateral Estilo Google Search */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #DADCE0;
        width: 400px !important;
    }
    section[data-testid="stSidebar"] * { color: #202124 !important; }

    /* Zona de Drop de Arquivo */
    div[data-testid="stFileUploadDropzone"] {
        border: 2px dashed #4285F4 !important;
        background-color: #F1F3F4 !important;
        border-radius: 12px !important;
    }

    /* Cards de Pedidos */
    .pedido-card {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #DADCE0;
        border-left: 12px solid #34A853 !important; /* Verde Google */
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .pedido-alerta { 
        border-left: 12px solid #EA4335 !important; /* Vermelho Google */
        background-color: #FEEEEE !important; 
    }

    /* Botões */
    .stButton>button {
        background-color: #1A73E8 !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        height: 3em;
        width: 100%;
    }
    
    /* Tags de Vendedor */
    .vendedor-tag {
        background-color: #E8F0FE;
        color: #1967D2 !important;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 13px;
        display: inline-block;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. TÍTULO PRINCIPAL ---
st.title("🚚 ExpedFlow Pro")
st.markdown("---")

# --- 5. BARRA LATERAL (ENTRADA ESTILO GOOGLE) ---
with st.sidebar:
    st.header("🔎 Entrada de Carga")
    
    # Receptor de Imagem 1: Arrastar
    arquivo_upload = st.file_uploader("Arraste o print/foto aqui", type=['png', 'jpg', 'jpeg'])
    
    st.markdown("<p style='text-align:center; color:#70757a;'>OU</p>", unsafe_allow_html=True)
    
    # Receptor de Imagem 2: Ctrl+V (Receptor de texto invisível para o JS)
    buffer_colagem = st.text_input("Status do Print:", placeholder="Clique aqui e dê Ctrl+V", key="buffer_colagem")
    
    # Lógica de Captura Final
    final_img_blob = None
    if arquivo_upload:
        final_img_blob = arquivo_upload.read()
        st.success("✅ Arquivo pronto!")
    elif "data:image" in buffer_colagem:
        final_img_blob = base64.b64decode(buffer_colagem.split(",")[1])
        st.success("✅ Print capturado via Ctrl+V!")
        with st.expander("Ver Prévia"):
            st.image(final_img_blob)

    st.divider()
    
    # Formulário de Dados
    with st.form("form_entrada", clear_on_submit=True):
        n = st.text_input("Número da Nota Fiscal", placeholder="Ex: 10550")
        v = st.text_input("Vendedor", placeholder="Quem vendeu?")
        e = st.text_area("Observações (Endereço, Urgência)", placeholder="Mudar entrega para...")
        
        btn_salvar = st.form_submit_button("PESQUISAR E SALVAR")
        
        if btn_salvar and n:
            conn.cursor().execute(
                "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, endereco, anexo, status, ultima_atualizacao) VALUES (?,?,?,?,?,?)",
                (n, v, e, final_img_blob, 'PENDENTE', datetime.now())
            )
            conn.commit()
            st.success(f"Nota {n} salva na fila!")
            st.rerun()

# --- 6. PAINEL DE GESTÃO (KANBAN) ---
df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY ultima_atualizacao DESC", conn)
col_mesa, col_patio = st.columns([1.5, 1])

with col_mesa:
    st.subheader("⏳ NA MESA (Fila de Triagem)")
    pendentes = df[df['status'] == 'PENDENTE']
    
    if pendentes.empty:
        st.info("Nenhuma nota aguardando.")
    else:
        for _, row in pendentes.iterrows():
            # Alerta visual automático
            is_alerta = any(word in str(row['endereco']).lower() for word in ['mudar', 'urgente', 'trocar', 'atenção'])
            estilo = "pedido-alerta" if is_alerta else ""
            
            with st.container():
                st.markdown(f"""
                    <div class="pedido-card {estilo}">
                        <div class="vendedor-tag">Vendedor: {row['vendedor']}</div>
                        <h2 style='margin:0'>NF: #{row['id_nota']}</h2>
                        <p style='margin-top:10px; color:#3C4043 !important;'>{row['endereco']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if row['anexo']:
                    with st.expander("🖼️ Ver Anexo/Print"):
                        st.image(row['anexo'])
                
                if st.button(f"LIBERAR PARA CARGA #{row['id_nota']}", key=f"btn_{row['id_nota']}"):
                    conn.cursor().execute("UPDATE pedidos SET status = 'CONCLUIDO', ultima_atualizacao = ? WHERE id_nota = ?", (datetime.now(), row['id_nota']))
                    conn.commit()
                    st.rerun()

with col_patio:
    st.subheader("✅ NO PÁTIO (Carregado)")
    concluidos = df[df['status'] == 'CONCLUIDO']
    if not concluidos.empty:
        st.table(concluidos[['id_nota', 'vendedor']].head(15))
    else:
        st.write("Aguardando primeiras cargas.")
