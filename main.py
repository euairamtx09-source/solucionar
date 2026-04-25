import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Função para garantir que o banco e a tabela existam
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

# Inicializa o banco
conn = init_db()

st.set_page_config(layout="wide", page_title="ExpedFlow")
st.title("🚀 ExpedFlow: Gestão de Notas")

# Formulário lateral para entrada manual (enquanto não ligamos o Zap)
st.sidebar.header("➕ Novo Pedido")
with st.sidebar.form("novo_pedido"):
    nota = st.text_input("Número da Nota")
    vend = st.text_input("Vendedor")
    end = st.text_area("Endereço/Observações")
    submit = st.form_submit_button("Cadastrar")
    
    if submit and nota:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO pedidos (id_nota, vendedor, endereco, status, ultima_atualizacao) VALUES (?, ?, ?, ?, ?)",
                       (nota, vend, end, 'PENDENTE', datetime.now()))
        conn.commit()
        st.success(f"Nota {nota} salva!")
        st.rerun()

# Carregar dados para exibir
df = pd.read_sql_query("SELECT * FROM pedidos ORDER BY ultima_atualizacao DESC", conn)

# Organização em colunas
col1, col2 = st.columns(2)

with col1:
    st.header("📥 Notas Pendentes")
    pendentes = df[df['status'] == 'PENDENTE']
    if pendentes.empty:
        st.write("Nenhuma nota pendente.")
    for _, row in pendentes.iterrows():
        with st.container(border=True):
            st.subheader(f"Nota: {row['id_nota']}")
            st.write(f"**Vendedor:** {row['vendedor']}")
            st.info(f"**Info:** {row['endereco']}")
            if st.button(f"Concluir {row['id_nota']}", key=row['id_nota']):
                conn.cursor().execute("UPDATE pedidos SET status = 'CONCLUIDO' WHERE id_nota = ?", (row['id_nota'],))
                conn.commit()
                st.rerun()

with col2:
    st.header("✅ Concluídas (Carga)")
    concluidas = df[df['status'] == 'CONCLUIDO']
    st.dataframe(concluidas[['id_nota', 'vendedor', 'ultima_atualizacao']], use_container_width=True)
