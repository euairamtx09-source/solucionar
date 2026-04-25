import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="ExpedFlow Pro", page_icon="🚚")

# --- INICIALIZAÇÃO DO BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('expedicao.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id_nota TEXT PRIMARY KEY,
            vendedor TEXT,
            endereco TEXT,
            status TEXT DEFAULT 'PENDENTE',
            alerta_critico INTEGER DEFAULT 0,
            ultima_atualizacao DATETIME
        )
    ''')
    conn.commit()
    return conn

conn = init_db()

# --- ESTILIZAÇÃO CSS PERSONALIZADA (Design Profissional) ---
st.markdown("""
    <style>
    /* Estilo do Fundo e Layout Principal */
    .stApp { background-color: #f4f7f6; }
    .main .block-container { padding-top: 2rem; }

    /* Estilo da Barra Lateral (Menu de Entrada) */
    section[data-testid="stSidebar"] {
        background-color: #1a1c24;
        color: white;
    }
    section[data-testid="stSidebar"] .stMarkdown h1, h2, h3 { color: white !important; }
    section[data-testid="stSidebar"] .stTextInput label, .stTextArea label { color: #a1a1a1 !important; }
    div[data-testid="stForm"] { border: none; background: #262a33; padding: 20px; border-radius: 10px; }

    /* Estilo dos Cards de Pedido (Fila de Entrada) */
    .pedido-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
        border-left: 6px solid #4CAF50; /* Verde padrão */
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .pedido-card:hover { transform: translateY(-3px); }
    
    /* Estilo para Pedidos com ALERTA (Urgente/Mudança) */
    .pedido-alerta {
        border-left: 6px solid #f44336 !important; /* Vermelho alerta */
        background-color: #fff8f8;
    }
    .pedido-card h3 { margin-top: 0; color: #1a1c24; }
    .pedido-card p { color: #666; font-size: 14px; margin-bottom: 8px; }

    /* Estilo da Tabela de Concluídos (Pátio) */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        background-color: white;
        padding: 10px;
    }

    /* Estilo da Tag de Vendedor */
    .vendedor-tag {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CORPO DO APLICATIVO ---
st.title("🚚 ExpedFlow Pro")
st.write("Sua central de logística e expedição de notas fiscais.")
st.divider()

# Carregar dados atualizados
df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY ultima_atualizacao DESC", conn)

# Organização Visual em duas colunas grandes
col_entrada, col_concluido = st.columns([2, 1])

# --- COLUNA 1: FILA DE PROCESSAMENTO (Sua Mesa) ---
with col_entrada:
    st.header("⏳ Na Mesa (Triagem)")
    pedidos_pendentes = df[df['status'] == 'PENDENTE']
    
    if pedidos_pendentes.empty:
        st.info("Nenhuma nota aguardando na fila. Tudo limpo!")
    else:
        for i, row in pedidos_pendentes.iterrows():
            # Identificação inteligente de urgência
            palavras_criticas = ['mudar', 'trocar', 'urgente', 'endereço']
            class_alerta = "pedido-alerta" if any(palavra in row['endereco'].lower() for palavra in palavras_criticas) else ""
            
            # Renderização do Card Estilizado
            st.markdown(f"""
                <div class="pedido-card {class_alerta}">
                    <div class="vendedor-tag">{row['vendedor'].upper()}</div>
                    <h3>Nota Fiscal: #{row['id_nota']}</h3>
                    <p><strong>Info/Endereço:</strong> {row['endereco']}</p>
                    <p style='font-size: 11px; color: #999; margin-top:10px;'>
                        Cadastrado em: {row['ultima_atualizacao']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Botão de Ação (Abaixo do card html)
            if st.button(f"Liberar Nota #{row['id_nota']} para o Pátio", key=f"btn_{row['id_nota']}", use_container_width=True):
                cursor = conn.cursor()
                cursor.execute("UPDATE pedidos SET status = 'CONCLUIDO', ultima_atualizacao = ? WHERE id_nota = ?", (datetime.now(), row['id_nota']))
                conn.commit()
                st.rerun()

# --- COLUNA 2: HISTÓRICO DE SAÍDA (O Pátio) ---
with col_concluido:
    st.header("✅ No Pátio (Carregamento)")
    pedidos_concluidos = df[df['status'] == 'CONCLUIDO']
    
    if pedidos_concluidos.empty:
        st.write("Nenhuma nota concluída hoje.")
    else:
        # Exibição em uma tabela limpa e profissional
        st.dataframe(pedidos_concluidos[['id_nota', 'vendedor', 'ultima_atualizacao']], use_container_width=True)

# --- BARRA LATERAL (ENTRADA DE DADOS PRO) ---
with st.sidebar:
    st.header("➕ Lançar Nota")
    st.write("Use este formulário para adicionar notas manualmente enquanto não conectamos o WhatsApp.")
    
    with st.form("form_add_nota", clear_on_submit=True):
        input_nota = st.text_input("Número da NF", placeholder="Ex: 12345")
        input_vendedor = st.text_input("Nome do Vendedor", placeholder="Ex: João")
        input_endereco = st.text_area("Observações ou Mudança de Endereço", placeholder="Ex: Mudar entrega para Rua X...")
        
        btn_salvar = st.form_submit_button("Salvar na Fila")
        
        if btn_salvar and input_nota:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO pedidos (id_nota, vendedor, endereco, status, ultima_atualizacao) VALUES (?,?,?,?,?)",
                               (input_nota, input_vendedor, input_endereco, 'PENDENTE', datetime.now()))
                conn.commit()
                st.success(f"Nota Fiscal {input_nota} cadastrada com sucesso!")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error(f"Erro: A nota {input_nota} já está cadastrada no sistema.")
