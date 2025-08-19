from supabase import create_client
import streamlit as st
import os

# -------------------
# Conexão com Supabase
# -------------------
url = os.getenv("https://qanworhvskscqcwbqnqx.supabase.co")
key = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFhbndvcmh2c2tzY3Fjd2JxbnF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU2MzI1MDYsImV4cCI6MjA3MTIwODUwNn0.3OJLnb1l1ag6HG8dTw6rsigsrulgSkmIUA7yaknj740")
supabase = create_client(url, key)

# -------------------
# Funções Auxiliares
# -------------------
def insert_data(table, data):
    supabase.table(table).insert(data).execute()

def get_data(table):
    res = supabase.table(table).select("*").execute()
    return res.data if res.data else []

def update_data(table, record_id, new_data):
    supabase.table(table).update(new_data).eq("id", record_id).execute()

# -------------------
# Estilo Customizado
# -------------------
st.markdown(
    """
    <style>
    body {
        background-color: #f7f9fc;
    }
    .main {
        background-color: #f7f9fc;
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .title {
        font-size: 22px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    .sub {
        font-size: 14px;
        color: #7f8c8d;
        margin-bottom: 15px;
    }
    .highlight {
        font-size: 18px;
        font-weight: bold;
        color: #27ae60;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------
# Streamlit Interface
# -------------------
st.markdown("<h1 style='color:#34495e;'>💰 Controle Financeiro - Eu & Minha Esposa</h1>", unsafe_allow_html=True)

tabs = st.tabs(["📉 Despesas", "📈 Rendas", "🎯 Metas", "📊 Orçamentos", "👥 Usuários"])

# -------------------
# 1. DESPESAS
# -------------------
with tabs[0]:
    st.markdown("<div class='card'><div class='title'>Cadastrar Despesa</div>", unsafe_allow_html=True)

    date = st.date_input("Data")
    category = st.text_input("Categoria")
    description = st.text_input("Descrição")
    value = st.number_input("Valor", min_value=0.0, step=0.01)

    if st.button("➕ Adicionar Despesa"):
        insert_data("expenses", {
            "date": str(date),
            "category": category,
            "description": description,
            "value": value
        })
        st.success("✅ Despesa adicionada com sucesso!")

    st.markdown("</div>", unsafe_allow_html=True)

    # Listagem
    st.markdown("<div class='card'><div class='title'>📋 Despesas Registradas</div>", unsafe_allow_html=True)
    data = get_data("expenses")
    if data:
        for item in data:
            st.markdown(
                f"""
                <div class='sub'>🗓 {item['date']} | <b>{item['category']}</b> - {item['description']}  
                <span class='highlight'>R$ {item['value']:.2f}</span></div>
                """,
                unsafe_allow_html=True
            )
            # Opção de edição
            if st.button(f"✏️ Editar #{item['id']}"):
                new_value = st.number_input("Novo Valor", value=item["value"], step=0.01, key=f"val_{item['id']}")
                if st.button(f"Salvar {item['id']}", key=f"save_{item['id']}"):
                    update_data("expenses", item["id"], {"value": new_value})
                    st.success("✅ Atualizado!")
    else:
        st.info("Nenhuma despesa registrada ainda.")
    st.markdown("</div>", unsafe_allow_html=True)
