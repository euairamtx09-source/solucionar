import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import base64
import io

# --- 1. CONFIGURAÇÃO DA PÁGINA (Interface Limpa e Profissional) ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="🚚")

# --- 2. GESTÃO DE BANCO DE DADOS (Correção Automática de Colunas) ---
def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
    # Cria a tabela base se não existir
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
    # Tenta adicionar a coluna 'anexo' caso o usuário tenha um banco antigo
    try:
        cursor.execute("ALTER TABLE pedidos ADD COLUMN anexo BLOB")
    except:
        pass # Coluna já existe
    conn.commit()
    return conn

conn = init_db()

# --- 3. MÁGICA DO CTRL+V (JavaScript Integrado) ---
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
                    // Procura o input de texto específico para injetar a imagem
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

# --- 4. ESTILIZAÇÃO DE ALTO CONTRASTE (Adeus Tela Estourada) ---
st.markdown("""
    <style>
    /* Cores de Fundo e Texto */
    .stApp { background-color: #F8F9FA !important; }
    h1, h2, h3, p, span, label { color: #1A1A1A !important; font-weight: 700 !important; }
    
    /* Barra Lateral Estilo Google */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 2px solid #DADCE0;
        width: 420px !important;
    }
    section[data-testid="stSidebar"] * { color: #1A1A1A !important; }

    /* Cards de Pedidos (Kanban) */
    .pedido-card {
        background-color: #FFFFFF !important;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #DADCE0;
        border-left: 15px solid #34A853 !important; /* Verde Google */
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .pedido-alerta { 
        border-left: 15px solid #EA4335 !important; /* Vermelho Google */
        background-color: #FFF5F5 !important; 
    }

    /* Botão Salvar */
    .stButton>button {
        background-color: #1A73E8 !important;
        color: white !important;
        border-radius: 8px;
        height: 3.5em;
        font-weight: bold;
        border: none;
    }
    
    /* Tags de Vendedor */
    .vendedor-tag {
        background-color: #E8F0FE;
        color: #1967D2 !important;
        padding: 4px 12px;
        border-radius: 16px;
        display: inline-block;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. CABEÇALHO ---
st.title("🚚 ExpedFlow: Painel de Controle Operacional")
st.divider()

# --- 6. BARRA LATERAL (ENTRADA ESTILO GOOGLE IMAGENS) ---
with st.sidebar:
    st.header("📥 Entrada de Carga")
    
    # Opção A: Arrastar
    arquivo_upload = st.file_uploader("Arraste o arquivo aqui", type=['png', 'jpg', 'jpeg'])
    
    st.markdown("<p style='text-align:center; color:#70757a;'>OU</p>", unsafe_allow_html=True)
    
    # Opção B: Ctrl + V (Receptor)
    buffer_colagem = st.text_input("Status do Print:", placeholder="Clique aqui e dê Ctrl+V", key="buffer_colagem")
    
    final_img_blob = None
    if arquivo_upload:
        final_img_blob = arquivo_upload.read()
        st.success("✅ Arquivo detectado!")
    elif "data:image" in buffer_colagem:
        final_img_blob = base64.b64decode(buffer_colagem.split(",")[1])
        st.success("✅ Print colado com sucesso!")
        with st.expander("Ver Prévia do Print"):
            st.image(final_img_blob)

    st.divider()
    
    # Formulário de Cadastro
    with st.form("cadastro_agil", clear_on_submit=True):
        input_nota = st.text_input("Número da NF")
        input_vendedor = st.text_input("Vendedor")
        input_obs = st.text_area("Observações (Urgência, Endereço)")
        
        btn_salvar = st.form_submit_button("CADASTRAR E SALVAR")
        
        if btn_salvar and input_nota:
            try:
                conn.cursor().execute(
                    "INSERT OR REPLACE INTO pedidos (id_nota, vendedor, endereco, anexo, status, ultima_atualizacao) VALUES (?,?,?,?,?,?)",
                    (input_nota, input_vendedor, input_obs, final_img_blob, 'PENDENTE', datetime.now())
                )
                conn.commit()
                st.success(f"Nota {input_nota} salva!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# --- 7. PAINEL KANBAN (EXIBIÇÃO) ---
df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY ultima_atualizacao DESC", conn)
col_mesa, col_patio = st.columns([1.5, 1])

with col_mesa:
    st.subheader("📋 FILA DA MESA")
    pedidos_pendentes = df[df['status'] == 'PENDENTE']
    
    if pedidos_pendentes.empty:
        st.info("Nenhuma nota pendente.")
    else:
        for _, row in pedidos_pendentes.iterrows():
            # Identifica alertas (Urgência)
            is_alerta = any(w in str(row['endereco']).lower() for w in ['mudar', 'urgente', 'trocar', 'atenção'])
            estilo = "pedido-alerta" if is_alerta else ""
            
            with st.container():
                st.markdown(f"""
                    <div class="pedido-card {estilo}">
                        <div class="vendedor-tag">Vendedor: {row['vendedor']}</div>
                        <h2 style='margin: 0;'>Nota Fiscal: #{row['id_nota']}</h2>
                        <p style='margin-top: 10px; font-size: 16px;'>{row['endereco']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if row['anexo']:
                    with st.expander("🖼️ Ver Anexo/Print"):
                        st.image(row['anexo'])
                
                if st.button(f"LIBERAR #{row['id_nota']}", key=f"btn_{row['id_nota']}", use_container_width=True):
                    conn.cursor().execute("UPDATE pedidos SET status = 'CONCLUIDO', ultima_atualizacao = ? WHERE id_nota = ?", (datetime.now(), row['id_nota']))
                    conn.commit()
                    st.rerun()

with col_patio:
    st.subheader("✅ JÁ NO PÁTIO")
    concluidos = df[df['status'] == 'CONCLUIDO']
    if not concluidos.empty:
        # Exibe em tabela com contraste corrigido
        st.dataframe(concluidos[['id_nota', 'vendedor', 'ultima_atualizacao']], use_container_width=True)
    else:
        st.write("Aguardando carregamentos.")
