# Projeto 1 — Dashboard de Inteligência de Vendas
# Base Exata | Flask + SQLite

import sqlite3
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')


def get_db():
    """Retorna conexão com o banco SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabelas():
    """Cria as tabelas se não existirem."""
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            custo REAL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            data_venda DATE NOT NULL,
            status TEXT DEFAULT 'Concluída',
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        );
    ''')
    conn.commit()
    conn.close()


def banco_vazio():
    """Verifica se o banco está vazio."""
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM vendas').fetchone()[0]
    conn.close()
    return total == 0


def inicializar_banco():
    """Cria tabelas e popula com dados de demonstração se necessário."""
    criar_tabelas()
    if banco_vazio():
        from seed_data import popular_banco
        popular_banco(DATABASE)


inicializar_banco()


@app.route('/')
def dashboard():
    """Página principal com KPIs e narrativa do case."""
    conn = get_db()

    # Mês atual
    mes_atual = datetime.now().strftime('%Y-%m')

    # Faturamento do mês
    faturamento_mes = conn.execute('''
        SELECT COALESCE(SUM(quantidade * preco_unitario), 0)
        FROM vendas
        WHERE strftime('%Y-%m', data_venda) = ?
    ''', (mes_atual,)).fetchone()[0]

    # Ticket médio do mês
    dados_ticket = conn.execute('''
        SELECT COALESCE(AVG(quantidade * preco_unitario), 0),
               COUNT(*)
        FROM vendas
        WHERE strftime('%Y-%m', data_venda) = ?
    ''', (mes_atual,)).fetchone()
    ticket_medio = dados_ticket[0]
    total_vendas_mes = dados_ticket[1]

    # Total de produtos vendidos no mês (unidades)
    produtos_vendidos = conn.execute('''
        SELECT COALESCE(SUM(quantidade), 0)
        FROM vendas
        WHERE strftime('%Y-%m', data_venda) = ?
    ''', (mes_atual,)).fetchone()[0]

    # Margem média do mês
    margem_media = conn.execute('''
        SELECT COALESCE(
            AVG((v.preco_unitario - p.custo) / v.preco_unitario * 100), 0
        )
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        WHERE strftime('%Y-%m', v.data_venda) = ?
          AND v.preco_unitario > 0
    ''', (mes_atual,)).fetchone()[0]

    conn.close()

    return render_template('index.html',
                           faturamento_mes=faturamento_mes,
                           ticket_medio=ticket_medio,
                           produtos_vendidos=produtos_vendidos,
                           margem_media=margem_media,
                           total_vendas_mes=total_vendas_mes)


@app.route('/api/faturamento-diario')
def api_faturamento_diario():
    """API: faturamento diário dos últimos 30 dias."""
    conn = get_db()
    labels = []
    valores = []

    for i in range(29, -1, -1):
        data = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        label = (datetime.now() - timedelta(days=i)).strftime('%d/%m')
        labels.append(label)

        total = conn.execute(
            'SELECT COALESCE(SUM(quantidade * preco_unitario), 0) FROM vendas WHERE data_venda = ?',
            (data,)
        ).fetchone()[0]
        valores.append(round(float(total), 2))

    conn.close()
    return jsonify({'labels': labels, 'valores': valores})


@app.route('/api/top-produtos')
def api_top_produtos():
    """API: top 10 produtos por receita total."""
    conn = get_db()
    rows = conn.execute('''
        SELECT p.nome,
               ROUND(SUM(v.quantidade * v.preco_unitario), 2) AS receita
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY p.id, p.nome
        ORDER BY receita DESC
        LIMIT 10
    ''').fetchall()
    conn.close()

    return jsonify({
        'labels': [r['nome'] for r in rows],
        'valores': [r['receita'] for r in rows]
    })


@app.route('/api/categorias')
def api_categorias():
    """API: participação por categoria no faturamento total."""
    conn = get_db()
    rows = conn.execute('''
        SELECT p.categoria,
               ROUND(SUM(v.quantidade * v.preco_unitario), 2) AS receita
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY p.categoria
        ORDER BY receita DESC
    ''').fetchall()
    conn.close()

    return jsonify({
        'labels': [r['categoria'] for r in rows],
        'valores': [r['receita'] for r in rows]
    })


@app.route('/api/ultimas-vendas')
def api_ultimas_vendas():
    """API: últimas 10 vendas com detalhes."""
    conn = get_db()
    rows = conn.execute('''
        SELECT v.id,
               p.nome AS produto,
               p.categoria,
               v.quantidade,
               v.preco_unitario,
               ROUND(v.quantidade * v.preco_unitario, 2) AS total,
               v.data_venda,
               v.status
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        ORDER BY v.data_venda DESC, v.id DESC
        LIMIT 10
    ''').fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])


if __name__ == '__main__':
    app.run(debug=True)
