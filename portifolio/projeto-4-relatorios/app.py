# Projeto 4 — Automação de Relatórios
# Base Exata | Flask + SQLite

import sqlite3
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify

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
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            margem_media REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            cidade TEXT NOT NULL,
            categoria_id INTEGER,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        );

        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY,
            data TEXT NOT NULL,
            categoria_id INTEGER NOT NULL,
            fornecedor_id INTEGER NOT NULL,
            quantidade_itens INTEGER NOT NULL,
            valor_total REAL NOT NULL,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id),
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
        );

        CREATE TABLE IF NOT EXISTS ticket_diario (
            id INTEGER PRIMARY KEY,
            data TEXT NOT NULL,
            num_transacoes INTEGER NOT NULL,
            ticket_medio REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS demo_meta (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()


def banco_vazio():
    """Verifica se o banco está vazio (sem vendas cadastradas)."""
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM vendas').fetchone()[0]
    conn.close()
    return total == 0


def inicializar_banco():
    """Cria tabelas e popula com dados de demonstração se necessário."""
    criar_tabelas()
    if banco_vazio():
        from seed_data import seed_database
        seed_database(DATABASE)


def atualizar_datas_demo():
    """Desloca datas de relatorios demo para manter meses recentes preenchidos."""
    conn = sqlite3.connect(DATABASE)
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS demo_meta (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
        ''')
        row = conn.execute('''
            SELECT MAX(max_data) FROM (
                SELECT MAX(data) AS max_data FROM vendas
                UNION ALL
                SELECT MAX(data) AS max_data FROM ticket_diario
            )
        ''').fetchone()
        max_data = row[0] if row else None
        if not max_data:
            conn.commit()
            return

        hoje = datetime.now().date()
        maior_data = datetime.strptime(max_data[:10], '%Y-%m-%d').date()
        dias = (hoje - maior_data).days

        if dias > 0:
            modificador = f"+{dias} days"
            conn.execute("UPDATE vendas SET data = date(data, ?)", (modificador,))
            conn.execute("UPDATE ticket_diario SET data = date(data, ?)", (modificador,))

        conn.execute(
            'INSERT OR REPLACE INTO demo_meta (chave, valor) VALUES (?, ?)',
            ('last_demo_refresh_date', hoje.isoformat())
        )
        conn.execute(
            'INSERT OR REPLACE INTO demo_meta (chave, valor) VALUES (?, ?)',
            ('last_max_data_detected', max_data)
        )
        conn.commit()
    finally:
        conn.close()


# Inicializa banco na importação do módulo
inicializar_banco()
atualizar_datas_demo()


@app.before_request
def refresh_demo_dates_once_per_day():
    hoje = datetime.now().strftime('%Y-%m-%d')
    if app.config.get('_demo_dates_checked_on') != hoje:
        atualizar_datas_demo()
        app.config['_demo_dates_checked_on'] = hoje


@app.context_processor
def inject_now():
    return {'data_atual': datetime.now().strftime('%d/%m/%Y')}


@app.route('/')
def dashboard():
    """Página principal do painel de relatórios gerenciais."""
    return render_template('index.html')


@app.route('/categorias')
def categorias():
    return render_template(
        'simple_page.html',
        title='Categorias',
        icon='bi-tags-fill',
        description='Visão preparada para detalhar participação por categoria, margem estimada e variações de compra e venda.'
    )


@app.route('/fornecedores')
def fornecedores():
    return render_template(
        'simple_page.html',
        title='Fornecedores',
        icon='bi-truck',
        description='Área para acompanhar fornecedores com maior volume, recorrência de pedidos e concentração de compras.'
    )


@app.route('/fechamento-mensal')
def fechamento_mensal():
    return render_template(
        'simple_page.html',
        title='Fechamento Mensal',
        icon='bi-calendar-month-fill',
        description='Resumo mensal para validar evolução de vendas, margem estimada e indicadores usados em reuniões gerenciais.'
    )


@app.route('/relatorio-executivo')
def relatorio_executivo():
    return render_template(
        'simple_page.html',
        title='Relatório Executivo',
        icon='bi-file-earmark-bar-graph-fill',
        description='Página de síntese para consolidar categorias, fornecedores, ticket e fechamento em uma leitura executiva.'
    )


@app.route('/api/resumo')
def api_resumo():
    """API JSON: 4 KPIs gerais do painel."""
    conn = get_db()

    total_vendas = conn.execute(
        'SELECT COALESCE(SUM(valor_total), 0) FROM vendas'
    ).fetchone()[0]

    total_ticket_registros = conn.execute(
        'SELECT COUNT(*) FROM ticket_diario'
    ).fetchone()[0]

    if total_ticket_registros == 0:
        ticket_medio = 0.0
    else:
        ticket_medio = conn.execute(
            'SELECT AVG(ticket_medio) FROM ticket_diario'
        ).fetchone()[0]

    categorias_ativas = conn.execute(
        'SELECT COUNT(DISTINCT categoria_id) FROM vendas'
    ).fetchone()[0]

    fornecedores_ativos = conn.execute(
        'SELECT COUNT(DISTINCT fornecedor_id) FROM vendas'
    ).fetchone()[0]

    conn.close()

    return jsonify({
        'total_vendas': round(total_vendas, 2),
        'ticket_medio': round(ticket_medio, 2),
        'categorias_ativas': categorias_ativas,
        'fornecedores_ativos': fornecedores_ativos
    })


@app.route('/api/vendas-por-categoria')
def api_vendas_por_categoria():
    """API JSON: total de vendas agrupado por categoria, com percentual."""
    conn = get_db()

    rows = conn.execute('''
        SELECT c.nome, COALESCE(SUM(v.valor_total), 0) AS total
        FROM categorias c
        LEFT JOIN vendas v ON v.categoria_id = c.id
        GROUP BY c.id, c.nome
        HAVING total > 0
        ORDER BY total DESC
    ''').fetchall()

    conn.close()

    total_geral = sum(row['total'] for row in rows)

    resultado = []
    for row in rows:
        percentual = (row['total'] / total_geral * 100) if total_geral > 0 else 0.0
        resultado.append({
            'nome': row['nome'],
            'total': round(row['total'], 2),
            'percentual': round(percentual, 1)
        })

    return jsonify(resultado)


@app.route('/api/ranking-fornecedores')
def api_ranking_fornecedores():
    """API JSON: top 10 fornecedores por volume de compras."""
    conn = get_db()

    rows = conn.execute('''
        SELECT f.nome, f.cidade,
               COALESCE(SUM(v.valor_total), 0) AS total_compras,
               COUNT(v.id) AS num_pedidos
        FROM fornecedores f
        INNER JOIN vendas v ON v.fornecedor_id = f.id
        GROUP BY f.id, f.nome, f.cidade
        ORDER BY total_compras DESC
        LIMIT 10
    ''').fetchall()

    conn.close()

    resultado = [
        {
            'nome': row['nome'],
            'cidade': row['cidade'],
            'total_compras': round(row['total_compras'], 2),
            'num_pedidos': row['num_pedidos']
        }
        for row in rows
    ]

    return jsonify(resultado)


@app.route('/api/evolucao-ticket')
def api_evolucao_ticket():
    """API JSON: evolução do ticket médio mensal nos últimos 12 meses."""
    # Mapeamento de número do mês para abreviação em PT-BR
    meses_pt = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
        5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }

    conn = get_db()

    rows = conn.execute('''
        SELECT strftime('%Y-%m', data) AS mes_ano,
               AVG(ticket_medio) AS media_ticket
        FROM ticket_diario
        GROUP BY mes_ano
        ORDER BY mes_ano ASC
    ''').fetchall()

    conn.close()

    resultado = []
    for row in rows:
        ano, mes = row['mes_ano'].split('-')
        label = f"{meses_pt[int(mes)]}/{ano[2:]}"
        resultado.append({
            'mes': label,
            'ticket_medio': round(row['media_ticket'], 2)
        })

    return jsonify(resultado)


@app.route('/api/fechamento-mensal')
def api_fechamento_mensal():
    """API JSON: fechamento de vendas e margem estimada dos últimos 12 meses."""
    meses_pt = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr',
        5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago',
        9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }

    conn = get_db()

    rows = conn.execute('''
        SELECT strftime('%Y-%m', v.data) AS mes_ano,
               SUM(v.valor_total) AS total_vendas,
               SUM(v.valor_total * c.margem_media) AS margem_estimada
        FROM vendas v
        INNER JOIN categorias c ON c.id = v.categoria_id
        GROUP BY mes_ano
        ORDER BY mes_ano ASC
    ''').fetchall()

    conn.close()

    resultado = []
    for row in rows:
        ano, mes = row['mes_ano'].split('-')
        label = f"{meses_pt[int(mes)]}/{ano[2:]}"
        resultado.append({
            'mes': label,
            'total_vendas': round(row['total_vendas'], 2),
            'margem_estimada': round(row['margem_estimada'], 2)
        })

    return jsonify(resultado)


if __name__ == '__main__':
    app.run(debug=True)
