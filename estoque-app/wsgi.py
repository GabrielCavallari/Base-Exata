"""
WSGI entry point — Gunicorn usa este arquivo.
Inicializa o banco e popula com dados demo automaticamente.
"""

import sqlite3
import os
from app import app, init_db, DATABASE

# Inicializar banco
init_db()

# Seed se estiver vazio
db_check = sqlite3.connect(DATABASE)
count = db_check.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
db_check.close()

if count == 0:
    from seed import seed_demo_data
    seed_demo_data(DATABASE)
    print("✅ Dados de demonstração inseridos!")
