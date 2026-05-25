"""
WSGI entry point — Gunicorn usa este arquivo.
Inicializa o banco e popula com dados demo automaticamente.
Usa file lock para evitar que múltiplos workers do Gunicorn
executem o seed simultaneamente (race condition).
"""

import sqlite3
import os
import fcntl
from app import app, init_db, DATABASE

LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".seed.lock")


def safe_init():
    """Inicializa o banco e roda o seed de forma segura (com lock)."""
    init_db()

    lock_fd = open(LOCK_FILE, "w")
    try:
        # Lock exclusivo — apenas um worker executa o seed por vez
        fcntl.flock(lock_fd, fcntl.LOCK_EX)

        db_check = sqlite3.connect(DATABASE)
        count = db_check.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
        db_check.close()

        if count == 0:
            from seed import seed_demo_data
            seed_demo_data(DATABASE)
            print("✅ Dados de demonstração inseridos!")
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


safe_init()
