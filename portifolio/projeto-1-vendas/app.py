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

        CREATE TABLE IF NOT EXISTS demo_meta (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
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


def atualizar_datas_demo():
    """Desloca datas de vendas demo para manter graficos recentes preenchidos."""
    conn = sqlite3.connect(DATABASE)
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS demo_meta (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
        ''')
        row = conn.execute('SELECT MAX(data_venda) FROM vendas').fetchone()
        max_data = row[0] if row else None
        if not max_data:
            conn.commit()
            return

        hoje = datetime.now().date()
        maior_data = datetime.strptime(max_data[:10], '%Y-%m-%d').date()
        dias = (hoje - maior_data).days

        if dias > 0:
            conn.execute("UPDATE vendas SET data_venda = date(data_venda, ?)", (f"+{dias} days",))

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


def badge_status(status):
    classes = {
        'Concluída': 'badge-entrada',
        'Cancelada': 'badge-saida',
        'Em processamento': 'badge-alerta',
    }
    return f'<span class="badge {classes.get(status, "bg-light text-dark")}">{status}</span>'


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


@app.route('/faturamento')
def faturamento():
    conn = get_db()
    rows = conn.execute('''
        SELECT data_venda,
               COUNT(*) AS pedidos,
               SUM(quantidade) AS unidades,
               SUM(quantidade * preco_unitario) AS receita
        FROM vendas
        WHERE data_venda >= date('now', '-29 days')
        GROUP BY data_venda
        ORDER BY data_venda
    ''').fetchall()
    total = sum(row['receita'] or 0 for row in rows)
    pedidos = sum(row['pedidos'] or 0 for row in rows)
    melhor_dia = max(rows, key=lambda row: row['receita'] or 0) if rows else None
    conn.close()

    return render_template(
        'simple_page.html',
        title='Faturamento',
        icon='bi-currency-dollar',
        subtitle='Evolução de receita dos últimos 30 dias',
        description='Visão dedicada para acompanhar evolução de receita, ticket médio e períodos com maior impacto no caixa.',
        kpis=[
            {'label': 'Receita no período', 'value': format_brl(total), 'hint': 'Soma das vendas registradas no SQLite.', 'icon': 'bi-cash-stack'},
            {'label': 'Pedidos', 'value': pedidos, 'hint': 'Volume de vendas no recorte recente.', 'icon': 'bi-receipt'},
            {'label': 'Ticket médio', 'value': format_brl(total / pedidos if pedidos else 0), 'hint': 'Receita dividida pelo número de pedidos.', 'icon': 'bi-bag-check'},
            {'label': 'Melhor dia', 'value': datetime.strptime(melhor_dia['data_venda'], '%Y-%m-%d').strftime('%d/%m') if melhor_dia else '-', 'hint': format_brl(melhor_dia['receita']) if melhor_dia else 'Sem vendas no período.', 'icon': 'bi-calendar-check'},
        ],
        chart={
            'title': 'Faturamento diário',
            'type': 'line',
            'prefix': 'R$ ',
            'labels': [datetime.strptime(row['data_venda'], '%Y-%m-%d').strftime('%d/%m') for row in rows],
            'datasets': [{'label': 'Receita', 'data': [round(row['receita'] or 0, 2) for row in rows], 'borderColor': '#008080', 'backgroundColor': 'rgba(0,128,128,.14)', 'tension': .35, 'fill': True}]
        },
        insights=[
            {'title': 'Uso em reunião', 'text': 'Mostra rapidamente se o caixa recente está subindo, estável ou exigindo ação comercial.'},
            {'title': 'Próxima decisão', 'text': 'Cruzar os dias de pico com mix de produtos ajuda a planejar campanhas e compras.'},
        ],
        table={
            'title': 'Resumo diário',
            'headers': ['Data', 'Pedidos', 'Unidades', 'Receita'],
            'rows': [[datetime.strptime(row['data_venda'], '%Y-%m-%d').strftime('%d/%m/%Y'), row['pedidos'], row['unidades'], format_brl(row['receita'])] for row in reversed(rows[-10:])]
        }
    )


@app.route('/produtos')
def produtos():
    conn = get_db()
    rows = conn.execute('''
        SELECT p.nome, p.categoria,
               SUM(v.quantidade) AS unidades,
               SUM(v.quantidade * v.preco_unitario) AS receita,
               AVG((v.preco_unitario - p.custo) / v.preco_unitario * 100) AS margem,
               COUNT(v.id) AS vendas
        FROM produtos p
        JOIN vendas v ON v.produto_id = p.id
        GROUP BY p.id, p.nome, p.categoria
        ORDER BY receita DESC
        LIMIT 10
    ''').fetchall()
    resumo = conn.execute('''
        SELECT COUNT(*) AS produtos,
               COUNT(DISTINCT categoria) AS categorias,
               SUM(CASE WHEN custo > (
                   SELECT AVG(v.preco_unitario) FROM vendas v WHERE v.produto_id = produtos.id
               ) THEN 1 ELSE 0 END) AS margem_negativa
        FROM produtos
    ''').fetchone()
    conn.close()

    return render_template(
        'simple_page.html',
        title='Produtos',
        icon='bi-box-seam-fill',
        subtitle='Ranking de produtos por receita',
        description='Área para analisar mix, categorias, produtos mais vendidos e itens que exigem revisão de margem.',
        kpis=[
            {'label': 'Produtos cadastrados', 'value': resumo['produtos'], 'hint': 'SKUs simulados no banco demo.', 'icon': 'bi-boxes'},
            {'label': 'Categorias ativas', 'value': resumo['categorias'], 'hint': 'Agrupamentos comerciais do varejo.', 'icon': 'bi-tags'},
            {'label': 'Produto líder', 'value': rows[0]['nome'] if rows else '-', 'hint': format_brl(rows[0]['receita']) if rows else 'Sem vendas.', 'icon': 'bi-trophy'},
            {'label': 'Margem negativa', 'value': resumo['margem_negativa'] or 0, 'hint': 'Itens que pedem revisão de preço.', 'icon': 'bi-exclamation-triangle'},
        ],
        chart={
            'title': 'Top produtos por faturamento',
            'type': 'bar',
            'prefix': 'R$ ',
            'labels': [row['nome'] for row in rows[:8]],
            'datasets': [{'label': 'Receita', 'data': [round(row['receita'] or 0, 2) for row in rows[:8]], 'backgroundColor': '#1A365D'}]
        },
        insights=[
            {'title': 'Mix com foco', 'text': 'O ranking separa itens que puxam faturamento dos itens que apenas ocupam espaço no cadastro.'},
            {'title': 'Margem visível', 'text': 'A tela apoia uma conversa objetiva sobre preço, custo e prioridade de compra.'},
        ],
        table={
            'title': 'Produtos com maior impacto',
            'headers': ['Produto', 'Categoria', 'Unidades', 'Receita', 'Margem média'],
            'rows': [[row['nome'], row['categoria'], row['unidades'], format_brl(row['receita']), format_pct(row['margem'])] for row in rows]
        }
    )


@app.route('/ultimas-vendas')
def ultimas_vendas():
    conn = get_db()
    rows = conn.execute('''
        SELECT v.id, p.nome AS produto, p.categoria, v.quantidade, v.preco_unitario,
               v.quantidade * v.preco_unitario AS total, v.data_venda, v.status
        FROM vendas v
        JOIN produtos p ON p.id = v.produto_id
        ORDER BY v.data_venda DESC, v.id DESC
        LIMIT 15
    ''').fetchall()
    status_rows = conn.execute('''
        SELECT status, COUNT(*) AS total
        FROM vendas
        WHERE data_venda >= date('now', '-29 days')
        GROUP BY status
        ORDER BY total DESC
    ''').fetchall()
    hoje = conn.execute('''
        SELECT COUNT(*) AS pedidos, COALESCE(SUM(quantidade * preco_unitario), 0) AS receita
        FROM vendas
        WHERE data_venda = date('now')
    ''').fetchone()
    conn.close()

    return render_template(
        'simple_page.html',
        title='Últimas Vendas',
        icon='bi-clock-history',
        subtitle='Consulta operacional de vendas recentes',
        description='Lista operacional para consultar vendas recentes, status e comportamento de compra em ordem cronológica.',
        kpis=[
            {'label': 'Vendas hoje', 'value': hoje['pedidos'], 'hint': format_brl(hoje['receita']), 'icon': 'bi-calendar-day'},
            {'label': 'Último pedido', 'value': f"#{rows[0]['id']}" if rows else '-', 'hint': rows[0]['produto'] if rows else 'Sem registros.', 'icon': 'bi-receipt-cutoff'},
            {'label': 'Ticket recente', 'value': format_brl(sum(row['total'] for row in rows) / len(rows) if rows else 0), 'hint': 'Média das últimas vendas listadas.', 'icon': 'bi-calculator'},
            {'label': 'Status no período', 'value': len(status_rows), 'hint': 'Tipos de status encontrados nos últimos 30 dias.', 'icon': 'bi-ui-checks'},
        ],
        chart={
            'title': 'Distribuição por status nos últimos 30 dias',
            'type': 'doughnut',
            'labels': [row['status'] for row in status_rows],
            'datasets': [{'label': 'Vendas', 'data': [row['total'] for row in status_rows], 'backgroundColor': ['#008080', '#D35400', '#1A365D']}]
        },
        insights=[
            {'title': 'Rastreabilidade', 'text': 'A lista ajuda a demonstrar consulta operacional simples sem precisar de planilha paralela.'},
            {'title': 'Atenção comercial', 'text': 'Status cancelado ou em processamento fica evidente para acompanhamento rápido.'},
        ],
        table={
            'title': 'Vendas mais recentes',
            'headers': ['Data', 'Pedido', 'Produto', 'Qtd.', 'Total', 'Status'],
            'rows': [[datetime.strptime(row['data_venda'], '%Y-%m-%d').strftime('%d/%m/%Y'), f"#{row['id']}", row['produto'], row['quantidade'], format_brl(row['total']), badge_status(row['status'])] for row in rows]
        }
    )


@app.route('/relatorio-executivo')
def relatorio_executivo():
    conn = get_db()
    mes_atual = datetime.now().strftime('%Y-%m')
    categorias = conn.execute('''
        SELECT p.categoria,
               SUM(v.quantidade * v.preco_unitario) AS receita,
               SUM(v.quantidade) AS unidades,
               AVG((v.preco_unitario - p.custo) / v.preco_unitario * 100) AS margem
        FROM vendas v
        JOIN produtos p ON p.id = v.produto_id
        GROUP BY p.categoria
        ORDER BY receita DESC
    ''').fetchall()
    mes = conn.execute('''
        SELECT COALESCE(SUM(v.quantidade * v.preco_unitario), 0) AS receita,
               COUNT(*) AS pedidos,
               AVG((v.preco_unitario - p.custo) / v.preco_unitario * 100) AS margem
        FROM vendas v
        JOIN produtos p ON p.id = v.produto_id
        WHERE strftime('%Y-%m', v.data_venda) = ?
    ''', (mes_atual,)).fetchone()
    negativos = conn.execute('''
        SELECT COUNT(*) FROM produtos p
        WHERE p.custo > (SELECT AVG(v.preco_unitario) FROM vendas v WHERE v.produto_id = p.id)
    ''').fetchone()[0]
    conn.close()

    return render_template(
        'simple_page.html',
        title='Relatório Executivo',
        icon='bi-file-earmark-bar-graph-fill',
        subtitle='Resumo para apresentação de decisão',
        description='Resumo gerencial para apresentar faturamento, margem, produtos relevantes e recomendações de decisão.',
        kpis=[
            {'label': 'Receita do mês', 'value': format_brl(mes['receita']), 'hint': f"{mes['pedidos']} vendas no mês atual.", 'icon': 'bi-graph-up-arrow'},
            {'label': 'Margem média', 'value': format_pct(mes['margem']), 'hint': 'Estimativa com base em custo cadastrado.', 'icon': 'bi-percent'},
            {'label': 'Categoria líder', 'value': categorias[0]['categoria'] if categorias else '-', 'hint': format_brl(categorias[0]['receita']) if categorias else 'Sem vendas.', 'icon': 'bi-award'},
            {'label': 'Alertas de preço', 'value': negativos, 'hint': 'Produtos com custo acima do preço médio praticado.', 'icon': 'bi-bell'},
        ],
        chart={
            'title': 'Participação por categoria',
            'type': 'bar',
            'prefix': 'R$ ',
            'labels': [row['categoria'] for row in categorias],
            'datasets': [{'label': 'Receita', 'data': [round(row['receita'] or 0, 2) for row in categorias], 'backgroundColor': '#D35400'}]
        },
        insights=[
            {'title': 'Mensagem executiva', 'text': 'O dashboard transforma venda operacional em pauta de reunião: receita, margem, mix e alertas.'},
            {'title': 'Ação sugerida', 'text': 'Priorizar revisão dos itens de margem negativa e reforçar compra das categorias líderes.'},
        ],
        table={
            'title': 'Categorias para decisão',
            'headers': ['Categoria', 'Receita', 'Unidades', 'Margem média'],
            'rows': [[row['categoria'], format_brl(row['receita']), row['unidades'], format_pct(row['margem'])] for row in categorias]
        }
    )


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
