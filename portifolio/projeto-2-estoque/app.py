# Projeto 2 — Sistema de Gestão de Estoque
# Base Exata | Flask + SQLite

import sqlite3
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# Caminho absoluto para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')


def get_db():
    """Retorna conexão com o banco SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabelas():
    """Cria as tabelas se não existirem."""
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            categoria TEXT,
            quantidade_atual INTEGER DEFAULT 0,
            quantidade_minima INTEGER DEFAULT 10,
            preco_unitario REAL DEFAULT 0,
            unidade TEXT DEFAULT 'un'
        );

        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY,
            produto_id INTEGER,
            tipo TEXT,
            quantidade INTEGER,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            observacao TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        );
    ''')
    conn.commit()
    conn.close()


def banco_vazio():
    """Verifica se o banco está vazio (sem produtos cadastrados)."""
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM produtos').fetchone()[0]
    conn.close()
    return total == 0


def inicializar_banco():
    """Cria tabelas e popula com dados de demonstração se necessário."""
    criar_tabelas()
    if banco_vazio():
        from seed_data import popular_banco
        popular_banco(DATABASE)


# Inicializa banco na importação do módulo
inicializar_banco()


@app.route('/')
def dashboard():
    """Página principal com KPIs e gráfico de movimentações."""
    conn = get_db()

    total_produtos = conn.execute('SELECT COUNT(*) FROM produtos').fetchone()[0]

    valor_total = conn.execute(
        'SELECT COALESCE(SUM(quantidade_atual * preco_unitario), 0) FROM produtos'
    ).fetchone()[0]

    produtos_alerta = conn.execute(
        'SELECT COUNT(*) FROM produtos WHERE quantidade_atual < quantidade_minima'
    ).fetchone()[0]

    hoje = datetime.now().strftime('%Y-%m-%d')
    mov_hoje = conn.execute(
        "SELECT COUNT(*) FROM movimentacoes WHERE DATE(data_hora) = ?",
        (hoje,)
    ).fetchone()[0]

    conn.close()

    return render_template('index.html',
                           total_produtos=total_produtos,
                           valor_total=valor_total,
                           produtos_alerta=produtos_alerta,
                           mov_hoje=mov_hoje)


@app.route('/produtos')
def produtos():
    """Listagem de todos os produtos com status de estoque."""
    conn = get_db()
    lista_produtos = conn.execute(
        'SELECT * FROM produtos ORDER BY categoria, nome'
    ).fetchall()
    conn.close()
    return render_template('produtos.html', produtos=lista_produtos)


@app.route('/alertas')
def alertas():
    """Produtos abaixo do estoque mínimo, ordenados por urgência."""
    conn = get_db()
    lista_alertas = conn.execute('''
        SELECT *,
               (quantidade_minima - quantidade_atual) AS deficit
        FROM produtos
        WHERE quantidade_atual < quantidade_minima
        ORDER BY quantidade_atual ASC
    ''').fetchall()
    conn.close()
    return render_template('alertas.html', alertas=lista_alertas)


@app.route('/movimentacao', methods=['POST'])
def movimentacao():
    """Registra entrada ou saída de estoque e atualiza quantidade."""
    produto_id = request.form.get('produto_id', type=int)
    tipo = request.form.get('tipo')
    quantidade = request.form.get('quantidade', type=int)
    observacao = request.form.get('observacao', '')

    if not produto_id or tipo not in ('entrada', 'saida') or not quantidade or quantidade <= 0:
        return redirect(url_for('produtos'))

    conn = get_db()

    conn.execute(
        'INSERT INTO movimentacoes (produto_id, tipo, quantidade, observacao) VALUES (?, ?, ?, ?)',
        (produto_id, tipo, quantidade, observacao)
    )

    if tipo == 'entrada':
        conn.execute(
            'UPDATE produtos SET quantidade_atual = quantidade_atual + ? WHERE id = ?',
            (quantidade, produto_id)
        )
    else:
        conn.execute(
            'UPDATE produtos SET quantidade_atual = MAX(0, quantidade_atual - ?) WHERE id = ?',
            (quantidade, produto_id)
        )

    conn.commit()
    conn.close()

    return redirect(url_for('produtos'))


@app.route('/api/movimentacoes-semana')
def api_movimentacoes_semana():
    """API JSON: movimentações (entradas vs saídas) dos últimos 7 dias."""
    conn = get_db()
    labels = []
    entradas = []
    saidas = []

    for i in range(6, -1, -1):
        data = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        label = (datetime.now() - timedelta(days=i)).strftime('%d/%m')
        labels.append(label)

        qtd_entrada = conn.execute(
            "SELECT COALESCE(SUM(quantidade), 0) FROM movimentacoes WHERE tipo='entrada' AND DATE(data_hora) = ?",
            (data,)
        ).fetchone()[0]

        qtd_saida = conn.execute(
            "SELECT COALESCE(SUM(quantidade), 0) FROM movimentacoes WHERE tipo='saida' AND DATE(data_hora) = ?",
            (data,)
        ).fetchone()[0]

        entradas.append(int(qtd_entrada))
        saidas.append(int(qtd_saida))

    conn.close()

    return jsonify({'labels': labels, 'entradas': entradas, 'saidas': saidas})


if __name__ == '__main__':
    app.run(debug=True)
