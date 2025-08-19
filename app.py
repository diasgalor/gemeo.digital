import streamlit as st
import pandas as pd
import sqlite3
import os
import datetime

# Database setup
DB_FILE = 'finances.db'

def init_db():
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
            limit REAL
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
    conn.close()

# Initialize DB
if not os.path.exists(DB_FILE):
    init_db()

# Functions to interact with DB
def add_income(date, source, amount):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO incomes (date, source, amount) VALUES (?, ?, ?)', (date, source, amount))
    conn.commit()
    conn.close()

def add_expense(date, category, description, amount):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)', (date, category, description, amount))
    conn.commit()
    conn.close()

def set_budget(category, limit):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO budgets (category, limit) VALUES (?, ?)', (category, limit))
    conn.commit()
    conn.close()

def add_goal(name, target_amount, salary_percentage):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO goals (name, target_amount, current_amount, salary_percentage) VALUES (?, ?, 0, ?)', (name, target_amount, salary_percentage))
    conn.commit()
    conn.close()

def update_goal_current(name, current_amount):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE goals SET current_amount = ? WHERE name = ?', (current_amount, name))
    conn.commit()
    conn.close()

def get_total_income():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query('SELECT SUM(amount) as total FROM incomes', conn)
    conn.close()
    return df['total'][0] if not df.empty and df['total'][0] is not None else 0.0

def get_total_expenses():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query('SELECT SUM(amount) as total FROM expenses', conn)
    conn.close()
    return df['total'][0] if not df.empty and df['total'][0] is not None else 0.0

def get_expenses_by_category():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query('SELECT category, SUM(amount) as total FROM expenses GROUP BY category', conn)
    conn.close()
    return df

def get_budgets():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query('SELECT * FROM budgets', conn)
    conn.close()
    return df.set_index('category')['limit'].to_dict() if not df.empty else {}

def get_goals():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query('SELECT * FROM goals', conn)
    conn.close()
    return df

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
        st.bar_chart(expenses_df.set_index('category'))
    
    st.subheader("Avisos de Orçamento")
    budgets = get_budgets()
    for category, total in expenses_df.set_index('category')['total'].items():
        if category in budgets and total > budgets[category]:
            st.warning(f"Categoria '{category}' extrapolou o limite! Gasto: R$ {total:.2f} / Limite: R$ {budgets[category]:.2f}")
    
    st.subheader("Progresso dos Objetivos")
    goals_df = get_goals()
    if not goals_df.empty:
        for _, row in goals_df.iterrows():
            progress = (row['current_amount'] / row['target_amount']) * 100 if row['target_amount'] > 0 else 0
            st.progress(progress / 100)
            st.write(f"{row['name']}: {progress:.2f}% (Atual: R$ {row['current_amount']:.2f} / Meta: R$ {row['target_amount']:.2f})")

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
            st.success("Renda adicionada!")

# Expenses Tab
elif tabs == "Despesas":
    st.title("Gerenciar Despesas")
    
    with st.form("Adicionar Despesa"):
        date = st.date_input("Data", datetime.date.today())
        category = st.text_input("Categoria (ex: Alimentação)")
        description = st.text_input("Descrição")
        amount = st.number_input("Valor", min_value=0.0)
        submit = st.form_submit_button("Adicionar")
        if submit:
            add_expense(str(date), category, description, amount)
            st.success("Despesa adicionada!")

# Budgets Tab
elif tabs == "Orçamentos":
    st.title("Definir Orçamentos")
    
    with st.form("Definir Orçamento"):
        category = st.text_input("Categoria")
        limit = st.number_input("Limite Mensal", min_value=0.0)
        submit = st.form_submit_button("Salvar")
        if submit:
            set_budget(category, limit)
            st.success("Orçamento definido!")
    
    st.subheader("Orçamentos Atuais")
    budgets = get_budgets()
    for cat, lim in budgets.items():
        st.write(f"{cat}: R$ {lim:.2f}")

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
            st.success("Objetivo adicionado!")
    
    st.subheader("Atualizar Progresso")
    goals_df = get_goals()
    if not goals_df.empty:
        for _, row in goals_df.iterrows():
            with st.expander(row['name']):
                current = st.number_input(f"Valor Atual para {row['name']}", value=float(row['current_amount']), min_value=0.0)
                if st.button("Atualizar", key=row['name']):
                    update_goal_current(row['name'], current)
                    st.success("Progresso atualizado!")
