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


def format_brl(valor):
    return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_pct(valor):
    return f"{float(valor or 0):.1f}%".replace(".", ",")


@app.route('/')
def dashboard():
    """Página principal do painel de relatórios gerenciais."""
    return render_template('index.html')


@app.route('/categorias')
def categorias():
    conn = get_db()
    rows = conn.execute('''
        SELECT c.nome,
               c.margem_media,
               COUNT(v.id) AS registros,
               SUM(v.quantidade_itens) AS itens,
               SUM(v.valor_total) AS faturamento,
               SUM(v.valor_total * c.margem_media) AS margem_estimada
        FROM categorias c
        LEFT JOIN vendas v ON v.categoria_id = c.id
        GROUP BY c.id, c.nome, c.margem_media
        ORDER BY faturamento DESC
    ''').fetchall()
    total = sum(row['faturamento'] or 0 for row in rows)
    conn.close()

    return render_template(
        'simple_page.html',
        title='Categorias',
        icon='bi-tags-fill',
        subtitle='Faturamento por categoria',
        description='Visão para detalhar participação por categoria, margem estimada e variações de compra e venda.',
        kpis=[
            {'label': 'Faturamento total', 'value': format_brl(total), 'hint': 'Soma dos registros de venda cadastrados.', 'icon': 'bi-cash-stack'},
            {'label': 'Categoria líder', 'value': rows[0]['nome'] if rows else '-', 'hint': format_brl(rows[0]['faturamento']) if rows else 'Sem dados.', 'icon': 'bi-trophy'},
            {'label': 'Categorias', 'value': len(rows), 'hint': 'Grupos ativos no relatório.', 'icon': 'bi-tags'},
            {'label': 'Margem estimada', 'value': format_brl(sum(row['margem_estimada'] or 0 for row in rows)), 'hint': 'Cálculo simulado por margem média.', 'icon': 'bi-percent'},
        ],
        chart={
            'title': 'Participação por categoria',
            'type': 'bar',
            'prefix': 'R$ ',
            'labels': [row['nome'] for row in rows],
            'datasets': [{'label': 'Faturamento', 'data': [round(row['faturamento'] or 0, 2) for row in rows], 'backgroundColor': '#008080'}]
        },
        insights=[
            {'title': 'Leitura gerencial', 'text': 'A tela transforma vendas dispersas em categorias claras para reunião de fechamento.'},
            {'title': 'Ação sugerida', 'text': 'Comparar categoria líder com margem estimada para priorizar compra e negociação.'},
        ],
        table={
            'title': 'Categorias consolidadas',
            'headers': ['Categoria', 'Registros', 'Itens', 'Faturamento', 'Margem média', 'Margem estimada'],
            'rows': [[row['nome'], row['registros'], row['itens'], format_brl(row['faturamento']), format_pct((row['margem_media'] or 0) * 100), format_brl(row['margem_estimada'])] for row in rows]
        }
    )


@app.route('/fornecedores')
def fornecedores():
    conn = get_db()
    rows = conn.execute('''
        SELECT f.nome, f.cidade, c.nome AS categoria,
               COUNT(v.id) AS pedidos,
               SUM(v.quantidade_itens) AS itens,
               SUM(v.valor_total) AS total
        FROM fornecedores f
        JOIN categorias c ON c.id = f.categoria_id
        LEFT JOIN vendas v ON v.fornecedor_id = f.id
        GROUP BY f.id, f.nome, f.cidade, c.nome
        ORDER BY total DESC
        LIMIT 12
    ''').fetchall()
    cidades = conn.execute('SELECT COUNT(DISTINCT cidade) FROM fornecedores').fetchone()[0]
    conn.close()

    return render_template(
        'simple_page.html',
        title='Fornecedores',
        icon='bi-truck',
        subtitle='Ranking de fornecedores por volume',
        description='Área para acompanhar fornecedores com maior volume, recorrência de pedidos e concentração de compras.',
        kpis=[
            {'label': 'Fornecedor líder', 'value': rows[0]['nome'] if rows else '-', 'hint': format_brl(rows[0]['total']) if rows else 'Sem dados.', 'icon': 'bi-truck-front'},
            {'label': 'Pedidos analisados', 'value': sum(row['pedidos'] or 0 for row in rows), 'hint': 'Pedidos dos fornecedores listados.', 'icon': 'bi-receipt'},
            {'label': 'Cidades', 'value': cidades, 'hint': 'Origem dos fornecedores cadastrados.', 'icon': 'bi-geo-alt'},
            {'label': 'Concentração top 3', 'value': format_brl(sum(row['total'] or 0 for row in rows[:3])), 'hint': 'Volume concentrado nos maiores fornecedores.', 'icon': 'bi-diagram-3'},
        ],
        chart={
            'title': 'Top fornecedores',
            'type': 'bar',
            'prefix': 'R$ ',
            'labels': [row['nome'] for row in rows[:8]],
            'datasets': [{'label': 'Compras', 'data': [round(row['total'] or 0, 2) for row in rows[:8]], 'backgroundColor': '#1A365D'}]
        },
        insights=[
            {'title': 'Negociação', 'text': 'O ranking ajuda a identificar fornecedores com peso real na operação.'},
            {'title': 'Risco de dependência', 'text': 'Alta concentração nos três primeiros pode orientar plano de cotação alternativa.'},
        ],
        table={
            'title': 'Fornecedores priorizados',
            'headers': ['Fornecedor', 'Cidade', 'Categoria', 'Pedidos', 'Itens', 'Total'],
            'rows': [[row['nome'], row['cidade'], row['categoria'], row['pedidos'], row['itens'], format_brl(row['total'])] for row in rows]
        }
    )


@app.route('/fechamento-mensal')
def fechamento_mensal():
    conn = get_db()
    rows = conn.execute('''
        SELECT strftime('%Y-%m', v.data) AS mes,
               COUNT(v.id) AS registros,
               SUM(v.quantidade_itens) AS itens,
               SUM(v.valor_total) AS vendas,
               SUM(v.valor_total * c.margem_media) AS margem
        FROM vendas v
        JOIN categorias c ON c.id = v.categoria_id
        GROUP BY mes
        ORDER BY mes DESC
        LIMIT 12
    ''').fetchall()
    rows = list(reversed(rows))
    ticket = conn.execute('SELECT AVG(ticket_medio) FROM ticket_diario WHERE data >= date("now", "-29 days")').fetchone()[0]
    conn.close()

    return render_template(
        'simple_page.html',
        title='Fechamento Mensal',
        icon='bi-calendar-month-fill',
        subtitle='Fechamento dos últimos 12 meses',
        description='Resumo mensal para validar evolução de vendas, margem estimada e indicadores usados em reuniões gerenciais.',
        kpis=[
            {'label': 'Mês atual', 'value': format_brl(rows[-1]['vendas'] if rows else 0), 'hint': rows[-1]['mes'] if rows else 'Sem dados.', 'icon': 'bi-calendar-check'},
            {'label': 'Margem atual', 'value': format_brl(rows[-1]['margem'] if rows else 0), 'hint': 'Estimativa pelo mix vendido.', 'icon': 'bi-piggy-bank'},
            {'label': 'Ticket 30 dias', 'value': format_brl(ticket), 'hint': 'Média recente do ticket diário.', 'icon': 'bi-receipt'},
            {'label': 'Meses fechados', 'value': len(rows), 'hint': 'Histórico disponível na demo.', 'icon': 'bi-calendar3'},
        ],
        chart={
            'title': 'Vendas e margem mensal',
            'type': 'bar',
            'prefix': 'R$ ',
            'labels': [datetime.strptime(row['mes'], '%Y-%m').strftime('%m/%y') for row in rows],
            'datasets': [
                {'label': 'Vendas', 'data': [round(row['vendas'] or 0, 2) for row in rows], 'backgroundColor': '#1A365D'},
                {'label': 'Margem estimada', 'data': [round(row['margem'] or 0, 2) for row in rows], 'backgroundColor': '#D35400'},
            ]
        },
        insights=[
            {'title': 'Fechamento mais rápido', 'text': 'A visão mensal reduz consolidação manual e acelera a reunião gerencial.'},
            {'title': 'Comparação simples', 'text': 'Vendas e margem lado a lado deixam claro se crescimento está vindo com rentabilidade.'},
        ],
        table={
            'title': 'Histórico mensal',
            'headers': ['Mês', 'Registros', 'Itens', 'Vendas', 'Margem estimada'],
            'rows': [[datetime.strptime(row['mes'], '%Y-%m').strftime('%m/%Y'), row['registros'], row['itens'], format_brl(row['vendas']), format_brl(row['margem'])] for row in reversed(rows)]
        }
    )


@app.route('/relatorio-executivo')
def relatorio_executivo():
    conn = get_db()
    resumo = conn.execute('''
        SELECT SUM(valor_total) AS vendas,
               COUNT(*) AS registros,
               SUM(quantidade_itens) AS itens
        FROM vendas
    ''').fetchone()
    categorias_top = conn.execute('''
        SELECT c.nome, SUM(v.valor_total) AS total
        FROM vendas v
        JOIN categorias c ON c.id = v.categoria_id
        GROUP BY c.id, c.nome
        ORDER BY total DESC
        LIMIT 6
    ''').fetchall()
    fornecedores_top = conn.execute('''
        SELECT f.nome, SUM(v.valor_total) AS total
        FROM vendas v
        JOIN fornecedores f ON f.id = v.fornecedor_id
        GROUP BY f.id, f.nome
        ORDER BY total DESC
        LIMIT 5
    ''').fetchall()
    conn.close()
    horas_manual = 12
    horas_automatizado = 1.5
    economia = (1 - horas_automatizado / horas_manual) * 100

    return render_template(
        'simple_page.html',
        title='Relatório Executivo',
        icon='bi-file-earmark-bar-graph-fill',
        subtitle='Resumo gerencial pronto para apresentação',
        description='Página de síntese para consolidar categorias, fornecedores, ticket e fechamento em uma leitura executiva.',
        kpis=[
            {'label': 'Vendas consolidadas', 'value': format_brl(resumo['vendas']), 'hint': f"{resumo['registros']} registros processados.", 'icon': 'bi-bar-chart'},
            {'label': 'Itens analisados', 'value': f"{resumo['itens']:,.0f}".replace(",", "."), 'hint': 'Volume operacional consolidado.', 'icon': 'bi-box-seam'},
            {'label': 'Economia simulada', 'value': format_pct(economia), 'hint': 'Comparação 12h manual vs. 1,5h automatizada.', 'icon': 'bi-lightning-charge'},
            {'label': 'Top fornecedor', 'value': fornecedores_top[0]['nome'] if fornecedores_top else '-', 'hint': format_brl(fornecedores_top[0]['total']) if fornecedores_top else 'Sem dados.', 'icon': 'bi-truck'},
        ],
        chart={
            'title': 'Categorias prioritárias',
            'type': 'doughnut',
            'prefix': 'R$ ',
            'labels': [row['nome'] for row in categorias_top],
            'datasets': [{'label': 'Vendas', 'data': [round(row['total'] or 0, 2) for row in categorias_top], 'backgroundColor': ['#1A365D', '#008080', '#D35400', '#234782', '#E8731A', '#6c757d']}]
        },
        insights=[
            {'title': 'Mensagem comercial', 'text': 'A demo evidencia ganho de rotina: menos tempo consolidando planilhas e mais tempo decidindo.'},
            {'title': 'Próxima ação', 'text': 'Automatizar a geração recorrente do relatório e revisar fornecedores com maior concentração.'},
        ],
        table={
            'title': 'Fornecedores para reunião',
            'headers': ['Prioridade', 'Fornecedor', 'Volume consolidado', 'Ação sugerida'],
            'rows': [[idx + 1, row['nome'], format_brl(row['total']), 'Renegociar condição' if idx < 2 else 'Monitorar recorrência'] for idx, row in enumerate(fornecedores_top)]
        }
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
