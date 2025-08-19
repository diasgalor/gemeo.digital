import streamlit as st
import pandas as pd
import sqlite3
import os
import datetime
import plotly.express as px

# Database setup
DB_FILE = 'finances.db'

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY,
                date TEXT,
                source TEXT,
                amount REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                date TEXT,
                category TEXT,
                description TEXT,
                amount REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY,
                category TEXT UNIQUE,
                budget_limit REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY,
                name TEXT,
                target_amount REAL,
                current_amount REAL,
                salary_percentage REAL
            )
        ''')
        
        conn.commit()
        st.success("Banco de dados inicializado com sucesso!")
    except sqlite3.Error as e:
        st.error(f"Erro ao inicializar o banco de dados: {e}")
    finally:
        conn.close()

# Initialize DB
if os.getenv("RESET_DB") == "true" or not os.path.exists(DB_FILE):
    init_db()
else:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='budgets'")
        if not cursor.fetchone():
            init_db()
        else:
            # Check if budgets table has the correct schema
            cursor.execute("PRAGMA table_info(budgets)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'budget_limit' not in columns:
                cursor.execute('DROP TABLE budgets')
                conn.commit()
                init_db()
    except sqlite3.Error as e:
        st.error(f"Erro ao verificar banco de dados: {e}")
        init_db()
    finally:
        conn.close()

# Functions to interact with DB
def add_income(date, source, amount):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO incomes (date, source, amount) VALUES (?, ?, ?)', (date, source, amount))
        conn.commit()
        st.success("Renda adicionada!")
    except sqlite3.Error as e:
        st.error(f"Erro ao adicionar renda: {e}")
    finally:
        conn.close()

def add_expense(date, category, description, amount):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)', (date, category, description, amount))
        conn.commit()
        st.success("Despesa adicionada!")
    except sqlite3.Error as e:
        st.error(f"Erro ao adicionar despesa: {e}")
    finally:
        conn.close()

def set_budget(category, budget_limit):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO budgets (category, budget_limit) VALUES (?, ?)', (category, budget_limit))
        conn.commit()
        st.success("Orçamento definido!")
    except sqlite3.Error as e:
        st.error(f"Erro ao definir orçamento: {e}")
    finally:
        conn.close()

def add_goal(name, target_amount, salary_percentage):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO goals (name, target_amount, current_amount, salary_percentage) VALUES (?, ?, 0, ?)', (name, target_amount, salary_percentage))
        conn.commit()
        st.success("Objetivo adicionado!")
    except sqlite3.Error as e:
        st.error(f"Erro ao adicionar objetivo: {e}")
    finally:
        conn.close()

def update_goal_current(name, current_amount):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('UPDATE goals SET current_amount = ? WHERE name = ?', (current_amount, name))
        conn.commit()
        st.success("Progresso atualizado!")
    except sqlite3.Error as e:
        st.error(f"Erro ao atualizar objetivo: {e}")
    finally:
        conn.close()

def get_total_income():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query('SELECT SUM(amount) as total FROM incomes', conn)
        return df['total'][0] if not df.empty and df['total'][0] is not None else 0.0
    except sqlite3.Error as e:
        st.error(f"Erro ao obter renda total: {e}")
        return 0.0
    finally:
        conn.close()

def get_total_expenses():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query('SELECT SUM(amount) as total FROM expenses', conn)
        return df['total'][0] if not df.empty and df['total'][0] is not None else 0.0
    except sqlite3.Error as e:
        st.error(f"Erro ao obter despesas totais: {e}")
        return 0.0
    finally:
        conn.close()

def get_expenses_by_category():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query('SELECT category, SUM(amount) as total FROM expenses GROUP BY category', conn)
        return df
    except sqlite3.Error as e:
        st.error(f"Erro ao obter despesas por categoria: {e}")
        return pd.DataFrame(columns=['category', 'total'])
    finally:
        conn.close()

def get_budgets():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query('SELECT * FROM budgets', conn)
        return df.set_index('category')['budget_limit'].to_dict() if not df.empty else {}
    except sqlite3.Error as e:
        st.error(f"Erro ao obter orçamentos: {e}")
        return {}
    finally:
        conn.close()

def get_goals():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query('SELECT * FROM goals', conn)
        return df
    except sqlite3.Error as e:
        st.error(f"Erro ao obter objetivos: {e}")
        return pd.DataFrame(columns=['name', 'target_amount', 'current_amount', 'salary_percentage'])
    finally:
        conn.close()

def get_existing_categories():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query('SELECT DISTINCT category FROM expenses', conn)
        return sorted(df['category'].tolist()) if not df.empty else []
    except sqlite3.Error as e:
        st.error(f"Erro ao obter categorias existentes: {e}")
        return []
    finally:
        conn.close()

def get_monthly_salary():
    return get_total_income()  # Adjust if you need monthly filtering

# Streamlit App
st.set_page_config(page_title="Finanças Familiares", layout="wide", initial_sidebar_state="expanded")

# Sidebar for navigation (mobile friendly)
st.sidebar.title("Navegação")
tabs = st.sidebar.radio("Seções", ["Dashboard", "Rendas", "Despesas", "Orçamentos", "Objetivos Financeiros"])

# Dashboard Tab
if tabs == "Dashboard":
    st.title("Dashboard Financeiro")
    
    total_income = get_total_income()
    total_expenses = get_total_expenses()
    balance = total_income - total_expenses
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Renda Total", f"R$ {total_income:.2f}")
    col2.metric("Despesas Total", f"R$ {total_expenses:.2f}")
    col3.metric("Saldo", f"R$ {balance:.2f}")
    
    st.subheader("Despesas por Categoria")
    expenses_df = get_expenses_by_category()
    if not expenses_df.empty:
        fig = px.pie(expenses_df, values='total', names='category', title='Distribuição de Despesas por Categoria')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma despesa registrada para exibir no gráfico.")
    
    st.subheader("Avisos de Orçamento")
    budgets = get_budgets()
    if budgets:
        for category, total in expenses_df.set_index('category')['total'].items():
            if category in budgets and total > budgets[category]:
                st.warning(f"Categoria '{category}' extrapolou o limite! Gasto: R$ {total:.2f} / Limite: R$ {budgets[category]:.2f}")
    else:
        st.info("Nenhum orçamento definido.")
    
    st.subheader("Progresso dos Objetivos")
    goals_df = get_goals()
    if not goals_df.empty:
        for _, row in goals_df.iterrows():
            progress = (row['current_amount'] / row['target_amount']) * 100 if row['target_amount'] > 0 else 0
            st.progress(progress / 100)
            st.write(f"{row['name']}: {progress:.2f}% (Atual: R$ {row['current_amount']:.2f} / Meta: R$ {row['target_amount']:.2f})")
    else:
        st.info("Nenhum objetivo financeiro definido.")

# Income Tab
elif tabs == "Rendas":
    st.title("Gerenciar Rendas")
    
    with st.form("Adicionar Renda"):
        date = st.date_input("Data", datetime.date.today())
        source = st.text_input("Fonte (ex: Salário)")
        amount = st.number_input("Valor", min_value=0.0)
        submit = st.form_submit_button("Adicionar")
        if submit:
            add_income(str(date), source, amount)

# Expenses Tab
elif tabs == "Despesas":
    st.title("Gerenciar Despesas")
    
    with st.form("Adicionar Despesa"):
        date = st.date_input("Data", datetime.date.today())
        existing_categories = get_existing_categories()
        category = st.selectbox("Categoria (ex: Alimentação)", options=existing_categories + ["Nova categoria"], index=len(existing_categories) if existing_categories else 0)
        if category == "Nova categoria":
            category = st.text_input("Digite a nova categoria")
        description = st.text_input("Descrição")
        amount = st.number_input("Valor", min_value=0.0)
        submit = st.form_submit_button("Adicionar")
        if submit:
            if category and category != "Nova categoria":
                add_expense(str(date), category, description, amount)
            else:
                st.error("Por favor, insira uma categoria válida.")

# Budgets Tab
elif tabs == "Orçamentos":
    st.title("Definir Orçamentos")
    
    with st.form("Definir Orçamento"):
        existing_categories = get_existing_categories()
        category = st.selectbox("Categoria", options=existing_categories + ["Nova categoria"], index=len(existing_categories) if existing_categories else 0)
        if category == "Nova categoria":
            category = st.text_input("Digite a nova categoria")
        budget_limit = st.number_input("Limite Mensal", min_value=0.0)
        submit = st.form_submit_button("Salvar")
        if submit:
            if category and category != "Nova categoria":
                set_budget(category, budget_limit)
            else:
                st.error("Por favor, insira uma categoria válida.")
    
    st.subheader("Orçamentos Atuais")
    budgets = get_budgets()
    if budgets:
        for cat, lim in budgets.items():
            st.write(f"{cat}: R$ {lim:.2f}")
    else:
        st.info("Nenhum orçamento definido.")

# Goals Tab
elif tabs == "Objetivos Financeiros":
    st.title("Objetivos Financeiros")
    
    monthly_salary = get_monthly_salary()
    
    with st.form("Adicionar Objetivo"):
        name = st.text_input("Nome do Objetivo (ex: Viagem)")
        target_amount = st.number_input("Valor Alvo", min_value=0.0)
        salary_percentage = st.slider("% do Salário para Guardar", 0, 100, 10) / 100.0
        monthly_saving = monthly_salary * salary_percentage
        st.info(f"Com {salary_percentage*100:.0f}% do salário, você guardaria R$ {monthly_saving:.2f} por mês.")
        submit = st.form_submit_button("Adicionar")
        if submit:
            add_goal(name, target_amount, salary_percentage)
    
    st.subheader("Atualizar Progresso")
    goals_df = get_goals()
    if not goals_df.empty:
        for _, row in goals_df.iterrows():
            with st.expander(row['name']):
                current = st.number_input(f"Valor Atual para {row['name']}", value=float(row['current_amount']), min_value=0.0)
                if st.button("Atualizar", key=row['name']):
                    update_goal_current(row['name'], current)
    else:
        st.info("Nenhum objetivo financeiro definido.")
