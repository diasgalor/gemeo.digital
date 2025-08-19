from supabase import create_client, Client
import os

# Lê URL e KEY do ambiente (secrets no Streamlit)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------
# Usuários
# ---------------------
def add_user(name, email):
    data = supabase.table("users").insert({"name": name, "email": email}).execute()
    return data

def get_users():
    data = supabase.table("users").select("*").execute()
    return data.data

# ---------------------
# Despesas
# ---------------------
def add_expense(user_id, date, category, description, amount):
    data = supabase.table("expenses").insert({
        "user_id": user_id,
        "date": date,
        "category": category,
        "description": description,
        "amount": amount
    }).execute()
    return data

def get_expenses(user_id=None):
    query = supabase.table("expenses").select("*")
    if user_id:
        query = query.eq("user_id", user_id)
    data = query.execute()
    return data.data

# ---------------------
# Rendas
# ---------------------
def add_income(user_id, date, source, amount):
    data = supabase.table("incomes").insert({
        "user_id": user_id,
        "date": date,
        "source": source,
        "amount": amount
    }).execute()
    return data

def get_incomes(user_id=None):
    query = supabase.table("incomes").select("*")
    if user_id:
        query = query.eq("user_id", user_id)
    data = query.execute()
    return data.data
