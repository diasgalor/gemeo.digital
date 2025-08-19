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
                name TEXT UNIQUE,
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
            # Check schema consistency
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

# Funções DB
def add_income(date, source, amount):
    if amount <= 0:
        st.error("O valor da renda deve ser maior que zero.")
        return
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
    if not category or amount <= 0:
        st.error("Informe uma categoria válida e valor maior que zero.")
        return
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
    if not category or budget_limit <= 0:
        st.error("Informe uma categoria válida e limite maior que zero.")
        return
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
    if not name or target_amount <= 0:
        st.error("Informe um objetivo válido e valor alvo maior que zero.")
        return
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO goals (name, target_amount, current_amount, salary_percentage) VALUES (?, ?, 0, ?)', (name, target_amount, salary_percentage))
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
    except sqlite3.Error:
        return 0.0
    finally:
        conn.close()

def get_total_expenses():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query('SELECT SUM(amount) as total FROM expenses', conn)
        return df['total'][0] if not df.empty and df['total'][0] is not None else 0.0
    except sqlite3.Error:
        return 0.0
    finally:
        conn.close()

def get_expenses_by_category():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query('SELECT category, SUM(amount) as total FROM expenses GROUP BY category', conn)
        return df
    except sqlite3.Error:
        return pd.DataFrame(columns=['category', 'total'])
    finally:
        conn.close()

def get_budgets():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query('SELECT * FROM budgets', conn)
        return df.set_index('category')['budget_limit'].to_dict() if not df.empty else {}
    except sqlite3.Error:
        return {}
    finally:
        conn.close()

def get_goals():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query('SELECT * FROM goals', conn)
        return df
    except sqlite3.Error:
        return pd.DataFrame(columns=['name', 'target_amount', 'current_amount', 'salary_percentage'])
    finally:
        conn.close()

def get_existing_categories():
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query('SELECT DISTINCT category FROM expenses', conn)
        return sorted(df['category'].tolist()) if not df.empty else []
    except sqlite3.Error:
        return []
    finally:
        conn.close()

def get_monthly_salary():
    return get_total_income()  # Ajustar se quiser filtrar por mês

# Streamlit App
st.set_page_config(page_title="Finanças Familiares", layout="wide", initial_sidebar_state="expanded")

# Sidebar
st.sidebar.title("Navegação")
tabs = st.sidebar.radio("Seções", ["Dashboard", "Rendas", "Despesas", "Orçamentos", "Objetivos Financeiros"])

# Dashboard
if tabs == "Dashboard":
    st.title("Dashboard Financeiro")
    
    total_income = get_total_income()
    total_expenses = get_total_expenses()
    balance = total_income - total_expenses
    
    st.subheader("Visão Geral Financeira")
    if total_income > 0:
        expense_ratio = min(total_expenses / total_income, 1.0)
        balance_ratio = max(balance / total_income, 0.0)
        
        st.metric("Renda Total", f"R$ {total_income:.2f}")
        st.metric("Despesas", f"R$ {total_expenses:.2f}")
        st.progress(expense_ratio, text=f"Despesas: {expense_ratio*100:.1f}%")
        
        if balance >= 0:
            st.success(f"Saldo Restante: R$ {balance:.2f} ({balance_ratio*100:.1f}%)")
        else:
            st.error(f"Saldo Negativo: R$ {balance:.2f}")
    else:
        st.info("Nenhuma renda registrada para exibir métricas.")
    
    # Gráfico de despesas
    st.subheader("Despesas por Categoria")
    expenses_df = get_expenses_by_category()
    if not expenses_df.empty:
        fig = px.pie(expenses_df, values='total', names='category', title='Distribuição de Despesas por Categoria')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma despesa registrada.")
    
    # Orçamentos
    st.subheader("Avisos de Orçamento")
    budgets = get_budgets()
    if budgets and not expenses_df.empty:
        for category, total in expenses_df.set_index('category')['total'].items():
            if category in budgets and total > budgets[category]:
                st.warning(f"Categoria '{category}' extrapolou o limite! Gasto: R$ {total:.2f} / Limite: R$ {budgets[category]:.2f}")
    else:
        st.info("Nenhum orçamento definido.")
    
    # Objetivos
    st.subheader("Progresso dos Objetivos")
    goals_df = get_goals()
    if not goals_df.empty:
        for _, row in goals_df.iterrows():
            progress = (row['current_amount'] / row['target_amount']) * 100 if row['target_amount'] > 0 else 0
            st.progress(progress / 100)
            st.write(f"{row['name']}: {progress:.2f}% (Atual: R$ {row['current_amount']:.2f} / Meta: R$ {row['target_amount']:.2f})")
    else:
        st.info("Nenhum objetivo definido.")

# Rendas
elif tabs == "Rendas":
    st.title("Gerenciar Rendas")
    with st.form("Adicionar Renda"):
        date = st.date_input("Data", datetime.date.today())
        source = st.text_input("Fonte (ex: Salário)")
        amount = st.number_input("Valor", min_value=0.0)
        if st.form_submit_button("Adicionar"):
            add_income(str(date), source, amount)

# Despesas
elif tabs == "Despesas":
    st.title("Gerenciar Despesas")
    with st.form("Adicionar Despesa"):
        date = st.date_input("Data", datetime.date.today())
        existing_categories = get_existing_categories()
        category = st.selectbox("Categoria", options=existing_categories + ["Nova categoria"])
        if category == "Nova categoria":
            category = st.text_input("Digite a nova categoria")
        description = st.text_input("Descrição")
        amount = st.number_input("Valor", min_value=0.0)
        if st.form_submit_button("Adicionar"):
            add_expense(str(date), category, description, amount)

# Orçamentos
elif tabs == "Orçamentos":
    st.title("Definir Orçamentos")
    with st.form("Definir Orçamento"):
        existing_categories = get_existing_categories()
        category = st.selectbox("Categoria", options=existing_categories + ["Nova categoria"])
        if category == "Nova categoria":
            category = st.text_input("Digite a nova categoria")
        budget_limit = st.number_input("Limite Mensal", min_value=0.0)
        if st.form_submit_button("Salvar"):
            set_budget(category, budget_limit)
    
    st.subheader("Orçamentos Atuais")
    budgets = get_budgets()
    if budgets:
        for cat, lim in budgets.items():
            st.write(f"{cat}: R$ {lim:.2f}")
    else:
        st.info("Nenhum orçamento definido.")

# Objetivos
elif tabs == "Objetivos Financeiros":
    st.title("Objetivos Financeiros")
    monthly_salary = get_monthly_salary()
    
    with st.form("Adicionar Objetivo"):
        name = st.text_input("Nome do Objetivo")
        target_amount = st.number_input("Valor Alvo", min_value=0.0)
        salary_percentage = st.slider("% do Salário para Guardar", 0, 100, 10) / 100.0
        monthly_saving = monthly_salary * salary_percentage
        st.info(f"Com {salary_percentage*100:.0f}% do salário, você guardaria R$ {monthly_saving:.2f} por mês.")
        if st.form_submit_button("Adicionar"):
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
        st.info("Nenhum objetivo definido.")
