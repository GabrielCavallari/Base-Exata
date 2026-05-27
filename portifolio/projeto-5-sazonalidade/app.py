# Projeto 5 — Análise de Sazonalidade e Demanda
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
    """Retorna uma conexão aberta com o banco de dados SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabelas():
    """Cria as tabelas necessárias no banco de dados SQLite se não existirem."""
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            unidade TEXT NOT NULL DEFAULT 'un'
        );

        CREATE TABLE IF NOT EXISTS vendas_diarias (
            id INTEGER PRIMARY KEY,
            produto_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            valor_unitario REAL NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        );

        CREATE TABLE IF NOT EXISTS previsoes (
            id INTEGER PRIMARY KEY,
            produto_id INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            quantidade_prevista INTEGER NOT NULL,
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
    """Verifica se o banco de dados está vazio (sem registros de vendas diárias)."""
    conn = get_db()
    cursor = conn.execute('SELECT COUNT(*) FROM vendas_diarias')
    total = cursor.fetchone()[0]
    conn.close()
    return total == 0


def inicializar_banco():
    """Cria as tabelas e popula com os dados simulados caso esteja vazio."""
    criar_tabelas()
    if banco_vazio():
        from seed_data import seed_database
        seed_database(DATABASE)


def atualizar_datas_demo():
    """Desloca historico sazonal demo para terminar na data atual."""
    conn = sqlite3.connect(DATABASE)
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS demo_meta (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
        ''')
        row = conn.execute('SELECT MAX(data) FROM vendas_diarias').fetchone()
        max_data = row[0] if row else None
        if not max_data:
            conn.commit()
            return

        hoje = datetime.now().date()
        maior_data = datetime.strptime(max_data[:10], '%Y-%m-%d').date()
        dias = (hoje - maior_data).days

        if dias > 0:
            conn.execute("UPDATE vendas_diarias SET data = date(data, ?)", (f"+{dias} days",))

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


# Inicializa o banco de dados no nível do módulo
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


MESES_PT = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}


def format_brl(valor):
    return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_num(valor):
    return f"{int(valor or 0):,}".replace(",", ".")


@app.route('/')
def index():
    """Renderiza a página principal do dashboard de sazonalidade."""
    return render_template('index.html')


@app.route('/produtos')
def produtos():
    conn = get_db()
    rows = conn.execute('''
        SELECT p.nome, p.categoria, p.unidade,
               SUM(v.quantidade) AS quantidade,
               SUM(v.quantidade * v.valor_unitario) AS valor,
               AVG(v.valor_unitario) AS preco_medio
        FROM produtos p
        JOIN vendas_diarias v ON v.produto_id = p.id
        WHERE v.data >= date('now', '-89 days')
        GROUP BY p.id, p.nome, p.categoria, p.unidade
        ORDER BY quantidade DESC
    ''').fetchall()
    total_qtd = sum(row['quantidade'] or 0 for row in rows)
    categorias = len({row['categoria'] for row in rows})
    conn.close()

    return render_template(
        'simple_page.html',
        title='Produtos',
        icon='bi-box-seam-fill',
        subtitle='Produtos com maior giro recente',
        description='Visão para analisar itens com maior giro, categorias sazonais e produtos que exigem planejamento de compra.',
        kpis=[
            {'label': 'Volume 90 dias', 'value': format_num(total_qtd), 'hint': 'Quantidade vendida no período recente.', 'icon': 'bi-boxes'},
            {'label': 'Produto líder', 'value': rows[0]['nome'] if rows else '-', 'hint': f"{format_num(rows[0]['quantidade'])} {rows[0]['unidade']}" if rows else 'Sem dados.', 'icon': 'bi-trophy'},
            {'label': 'Categorias', 'value': categorias, 'hint': 'Grupos com venda recente.', 'icon': 'bi-tags'},
            {'label': 'Receita 90 dias', 'value': format_brl(sum(row['valor'] or 0 for row in rows)), 'hint': 'Valor simulado das vendas recentes.', 'icon': 'bi-cash-stack'},
        ],
        chart={
            'title': 'Top produtos por quantidade vendida',
            'type': 'bar',
            'labels': [row['nome'] for row in rows[:8]],
            'datasets': [{'label': 'Quantidade', 'data': [row['quantidade'] for row in rows[:8]], 'backgroundColor': '#008080'}]
        },
        insights=[
            {'title': 'Compra orientada', 'text': 'O ranking mostra onde o estoque precisa de atenção antes de ruptura.'},
            {'title': 'Uso comercial', 'text': 'A tela demonstra planejamento de compra com base em giro real, não em percepção.'},
        ],
        table={
            'title': 'Produtos por tendência recente',
            'headers': ['Produto', 'Categoria', 'Unidade', 'Quantidade', 'Receita', 'Preço médio'],
            'rows': [[row['nome'], row['categoria'], row['unidade'], format_num(row['quantidade']), format_brl(row['valor']), format_brl(row['preco_medio'])] for row in rows]
        }
    )


@app.route('/previsao-demanda')
def previsao_demanda():
    conn = get_db()
    produto_rows = conn.execute('''
        SELECT p.nome, p.categoria,
               SUM(pr.quantidade_prevista) AS previsto_total,
               MAX(pr.quantidade_prevista) AS pico_produto
        FROM produtos p
        JOIN previsoes pr ON pr.produto_id = p.id
        GROUP BY p.id, p.nome, p.categoria
        ORDER BY previsto_total DESC
    ''').fetchall()
    mes_rows = conn.execute('''
        SELECT mes, SUM(quantidade_prevista) AS previsto
        FROM previsoes
        GROUP BY mes
        ORDER BY mes
    ''').fetchall()
    pico = max(mes_rows, key=lambda row: row['previsto']) if mes_rows else None
    conn.close()

    return render_template(
        'simple_page.html',
        title='Previsão de Demanda',
        icon='bi-graph-up-arrow',
        subtitle='Previsão mensal para compras',
        description='Área para detalhar demanda prevista por produto, mês e categoria antes de decisões de compra.',
        kpis=[
            {'label': 'Previsão anual', 'value': format_num(sum(row['previsto_total'] or 0 for row in produto_rows)), 'hint': 'Soma simulada das previsões mensais.', 'icon': 'bi-calendar4-range'},
            {'label': 'Mês de pico', 'value': MESES_PT[pico['mes']] if pico else '-', 'hint': f"{format_num(pico['previsto'])} unidades previstas" if pico else 'Sem dados.', 'icon': 'bi-graph-up-arrow'},
            {'label': 'Produto crítico', 'value': produto_rows[0]['nome'] if produto_rows else '-', 'hint': format_num(produto_rows[0]['previsto_total']) if produto_rows else 'Sem dados.', 'icon': 'bi-box-seam'},
            {'label': 'Categorias', 'value': len({row['categoria'] for row in produto_rows}), 'hint': 'Categorias na matriz de previsão.', 'icon': 'bi-tags'},
        ],
        chart={
            'title': 'Demanda prevista por mês',
            'type': 'line',
            'labels': [MESES_PT[row['mes']] for row in mes_rows],
            'datasets': [{'label': 'Unidades previstas', 'data': [row['previsto'] for row in mes_rows], 'borderColor': '#1A365D', 'backgroundColor': 'rgba(26,54,93,.14)', 'tension': .35, 'fill': True}]
        },
        insights=[
            {'title': 'Planejamento antes da ruptura', 'text': 'A previsão antecipa meses de maior compra e reduz decisão baseada apenas em histórico manual.'},
            {'title': 'Ação sugerida', 'text': 'Negociar os produtos de maior previsão antes dos meses de pico.'},
        ],
        table={
            'title': 'Previsão por produto',
            'headers': ['Produto', 'Categoria', 'Previsto anual', 'Pico mensal', 'Recomendação'],
            'rows': [[row['nome'], row['categoria'], format_num(row['previsto_total']), format_num(row['pico_produto']), 'Comprar com antecedência' if idx < 3 else 'Monitorar giro'] for idx, row in enumerate(produto_rows)]
        }
    )


@app.route('/sazonalidade-mensal')
def sazonalidade_mensal():
    conn = get_db()
    rows = conn.execute('''
        SELECT CAST(strftime('%m', data) AS INTEGER) AS mes,
               SUM(quantidade) AS quantidade,
               SUM(quantidade * valor_unitario) AS valor
        FROM vendas_diarias
        GROUP BY mes
        ORDER BY mes
    ''').fetchall()
    pico = max(rows, key=lambda row: row['quantidade']) if rows else None
    menor = min(rows, key=lambda row: row['quantidade']) if rows else None
    conn.close()

    return render_template(
        'simple_page.html',
        title='Sazonalidade Mensal',
        icon='bi-calendar-month-fill',
        subtitle='Meses de pico e vale de demanda',
        description='Resumo para comparar meses de pico, meses fracos e padrões recorrentes de venda.',
        kpis=[
            {'label': 'Mês de pico', 'value': MESES_PT[pico['mes']] if pico else '-', 'hint': format_num(pico['quantidade']) if pico else 'Sem dados.', 'icon': 'bi-arrow-up-circle'},
            {'label': 'Mês mais fraco', 'value': MESES_PT[menor['mes']] if menor else '-', 'hint': format_num(menor['quantidade']) if menor else 'Sem dados.', 'icon': 'bi-arrow-down-circle'},
            {'label': 'Volume histórico', 'value': format_num(sum(row['quantidade'] or 0 for row in rows)), 'hint': 'Quantidade acumulada por mês do ano.', 'icon': 'bi-bar-chart'},
            {'label': 'Receita histórica', 'value': format_brl(sum(row['valor'] or 0 for row in rows)), 'hint': 'Valor acumulado no histórico simulado.', 'icon': 'bi-currency-dollar'},
        ],
        chart={
            'title': 'Sazonalidade por mês do ano',
            'type': 'bar',
            'labels': [MESES_PT[row['mes']] for row in rows],
            'datasets': [
                {'label': 'Quantidade', 'data': [row['quantidade'] for row in rows], 'backgroundColor': '#008080'},
                {'label': 'Valor em R$', 'data': [round((row['valor'] or 0) / 10, 2) for row in rows], 'backgroundColor': '#D35400'},
            ]
        },
        insights=[
            {'title': 'Padrão recorrente', 'text': 'A leitura mensal deixa claro quando a operação precisa reforçar estoque e caixa.'},
            {'title': 'Ação sugerida', 'text': 'Preparar compras, espaço e campanha antes dos meses com maior demanda histórica.'},
        ],
        table={
            'title': 'Resumo mensal',
            'headers': ['Mês', 'Quantidade', 'Receita', 'Classificação'],
            'rows': [[MESES_PT[row['mes']], format_num(row['quantidade']), format_brl(row['valor']), 'Pico' if pico and row['mes'] == pico['mes'] else ('Vale' if menor and row['mes'] == menor['mes'] else 'Regular')] for row in rows]
        }
    )


@app.route('/relatorio-executivo')
def relatorio_executivo():
    conn = get_db()
    top_produtos = conn.execute('''
        SELECT p.nome, p.categoria,
               SUM(v.quantidade) AS quantidade,
               SUM(v.quantidade * v.valor_unitario) AS valor
        FROM produtos p
        JOIN vendas_diarias v ON v.produto_id = p.id
        WHERE v.data >= date('now', '-89 days')
        GROUP BY p.id, p.nome, p.categoria
        ORDER BY quantidade DESC
        LIMIT 6
    ''').fetchall()
    previsoes = conn.execute('''
        SELECT mes, SUM(quantidade_prevista) AS previsto
        FROM previsoes
        GROUP BY mes
        ORDER BY mes
    ''').fetchall()
    pico = max(previsoes, key=lambda row: row['previsto']) if previsoes else None
    conn.close()

    return render_template(
        'simple_page.html',
        title='Relatório Executivo',
        icon='bi-file-earmark-bar-graph-fill',
        subtitle='Recomendações de estoque e compra',
        description='Síntese gerencial para orientar compras, estoque e campanhas conforme a previsão de demanda.',
        kpis=[
            {'label': 'Produto prioritário', 'value': top_produtos[0]['nome'] if top_produtos else '-', 'hint': f"{format_num(top_produtos[0]['quantidade'])} un. nos últimos 90 dias" if top_produtos else 'Sem dados.', 'icon': 'bi-star'},
            {'label': 'Pico previsto', 'value': MESES_PT[pico['mes']] if pico else '-', 'hint': format_num(pico['previsto']) if pico else 'Sem dados.', 'icon': 'bi-calendar-event'},
            {'label': 'Receita recente', 'value': format_brl(sum(row['valor'] or 0 for row in top_produtos)), 'hint': 'Top produtos dos últimos 90 dias.', 'icon': 'bi-cash-stack'},
            {'label': 'Itens críticos', 'value': len(top_produtos[:3]), 'hint': 'Primeiros itens para plano de compra.', 'icon': 'bi-clipboard-check'},
        ],
        chart={
            'title': 'Produtos que puxam a demanda',
            'type': 'bar',
            'labels': [row['nome'] for row in top_produtos],
            'datasets': [{'label': 'Quantidade 90 dias', 'data': [row['quantidade'] for row in top_produtos], 'backgroundColor': '#1A365D'}]
        },
        insights=[
            {'title': 'Resumo executivo', 'text': 'A demo conecta histórico, previsão e recomendação de compra em uma mesma tela.'},
            {'title': 'Ação sugerida', 'text': 'Reservar orçamento e negociar entrega antes do mês de pico previsto.'},
        ],
        table={
            'title': 'Plano sugerido de estoque',
            'headers': ['Prioridade', 'Produto', 'Categoria', 'Giro recente', 'Ação sugerida'],
            'rows': [[idx + 1, row['nome'], row['categoria'], format_num(row['quantidade']), 'Reforçar compra' if idx < 3 else 'Monitorar semanalmente'] for idx, row in enumerate(top_produtos)]
        }
    )


@app.route('/api/resumo')
def api_resumo():
    """Retorna dados consolidados para os KPIs (últimos 30 dias em relação à data máxima)."""
    conn = get_db()
    
    # 1. Total de produtos cadastrados
    total_produtos = conn.execute('SELECT COUNT(*) FROM produtos').fetchone()[0]
    
    # 2. Obter a data máxima nas vendas para servir de âncora para os 30 dias (evitando KPIs zerados)
    max_date_row = conn.execute('SELECT MAX(data) FROM vendas_diarias').fetchone()
    
    if max_date_row and max_date_row[0]:
        max_date = datetime.strptime(max_date_row[0], '%Y-%m-%d')
    else:
        max_date = datetime.now()
        
    data_limite = (max_date - timedelta(days=29)).strftime('%Y-%m-%d')
    
    # 3. Total de vendas nos últimos 30 dias (quantidade * valor_unitario)
    total_vendas_30d = conn.execute('''
        SELECT COALESCE(SUM(quantidade * valor_unitario), 0.0)
        FROM vendas_diarias
        WHERE data >= ?
    ''', (data_limite,)).fetchone()[0]
    
    # 4. Ticket Médio Diário nos últimos 30 dias (Média dos faturamentos diários)
    ticket_medio_30d = conn.execute('''
        SELECT COALESCE(AVG(faturamento_diario), 0.0)
        FROM (
            SELECT SUM(quantidade * valor_unitario) AS faturamento_diario
            FROM vendas_diarias
            WHERE data >= ?
            GROUP BY data
        )
    ''', (data_limite,)).fetchone()[0]
    
    # 5. Produto mais vendido em volume de quantidade nos últimos 30 dias
    mais_vendido_row = conn.execute('''
        SELECT p.nome
        FROM vendas_diarias v
        JOIN produtos p ON v.produto_id = p.id
        WHERE v.data >= ?
        GROUP BY v.produto_id
        ORDER BY SUM(v.quantidade) DESC
        LIMIT 1
    ''', (data_limite,)).fetchone()
    
    produto_mais_vendido = mais_vendido_row[0] if mais_vendido_row else "Nenhum"
    
    conn.close()
    
    return jsonify({
        "total_produtos": total_produtos,
        "total_vendas_30d": round(total_vendas_30d, 2),
        "ticket_medio_30d": round(ticket_medio_30d, 2),
        "produto_mais_vendido": produto_mais_vendido
    })


@app.route('/api/sazonalidade-mensal')
def api_sazonalidade_mensal():
    """Retorna o volume e valor de vendas agregados por mês do ano (1 a 12) em PT-BR."""
    meses_pt = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    
    conn = get_db()
    rows = conn.execute('''
        SELECT CAST(strftime('%m', data) AS INTEGER) AS num_mes,
               COALESCE(SUM(quantidade), 0) AS total_qtd,
               COALESCE(SUM(quantidade * valor_unitario), 0.0) AS total_valor
        FROM vendas_diarias
        GROUP BY num_mes
        ORDER BY num_mes ASC
    ''').fetchall()
    conn.close()
    
    # Inicializa todos os 12 meses para evitar lacunas
    resultado = {i: {"mes": meses_pt[i], "quantidade": 0, "valor": 0.0} for i in range(1, 13)}
    
    for row in rows:
        m = row['num_mes']
        if m in resultado:
            resultado[m]['quantidade'] = int(row['total_qtd'])
            resultado[m]['valor'] = round(float(row['total_valor']), 2)
            
    return jsonify(list(resultado.values()))


@app.route('/api/top-produtos')
def api_top_produtos():
    """Retorna os 8 produtos com maior quantidade acumulada de vendas no período total."""
    conn = get_db()
    rows = conn.execute('''
        SELECT p.nome, p.categoria,
               COALESCE(SUM(v.quantidade), 0) AS quantidade_total,
               COALESCE(SUM(v.quantidade * v.valor_unitario), 0.0) AS valor_total
        FROM produtos p
        LEFT JOIN vendas_diarias v ON p.id = v.produto_id
        GROUP BY p.id, p.nome, p.categoria
        ORDER BY quantidade_total DESC
        LIMIT 8
    ''').fetchall()
    conn.close()
    
    resultado = [
        {
            "nome": row["nome"],
            "categoria": row["categoria"],
            "quantidade_total": int(row["quantidade_total"]),
            "valor_total": round(float(row["valor_total"]), 2)
        } for row in rows
    ]
    
    return jsonify(resultado)


@app.route('/api/evolucao-semanal')
def api_evolucao_semanal():
    """Retorna o histórico das últimas 12 semanas a partir dos dados do banco, do mais antigo ao mais recente."""
    conn = get_db()
    
    # Agrupa por ano-semana e pela segunda-feira correspondente
    rows = conn.execute('''
        SELECT
            strftime('%Y-%W', data) AS ano_semana,
            date(data, '-' || ((cast(strftime('%w', data) as integer) + 6) % 7) || ' days') AS segunda_feira,
            COALESCE(SUM(quantidade), 0) AS total_qtd,
            COALESCE(SUM(quantidade * valor_unitario), 0.0) AS total_valor
        FROM vendas_diarias
        GROUP BY ano_semana
        ORDER BY ano_semana DESC
        LIMIT 12
    ''').fetchall()
    
    conn.close()
    
    # Inverte para ficar cronológico (do mais antigo ao mais recente)
    rows_crescentes = list(reversed(rows))
    
    resultado = []
    for row in rows_crescentes:
        segunda_str = row['segunda_feira']
        dt = datetime.strptime(segunda_str, '%Y-%m-%d')
        semana_label = f"Sem {dt.strftime('%d/%m')}"
        
        resultado.append({
            "semana": semana_label,
            "quantidade": int(row['total_qtd']),
            "valor": round(float(row['total_valor']), 2)
        })
        
    return jsonify(resultado)


@app.route('/api/previsao-demanda')
def api_previsao_demanda():
    """Retorna a matriz de previsão mensal para todos os produtos que possuem previsão cadastrada."""
    meses_pt = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    
    conn = get_db()
    rows = conn.execute('''
        SELECT p.id AS produto_id, p.nome AS produto_nome, p.categoria AS produto_categoria,
               prev.mes AS prev_mes, prev.quantidade_prevista AS prev_qtd
        FROM produtos p
        LEFT JOIN previsoes prev ON p.id = prev.produto_id
        ORDER BY p.nome, prev.mes
    ''').fetchall()
    conn.close()
    
    # Agrupa dados por produto
    produtos_dict = {}
    for row in rows:
        prod_id = row['produto_id']
        if prod_id not in produtos_dict:
            produtos_dict[prod_id] = {
                "produto": row['produto_nome'],
                "categoria": row['produto_categoria'],
                "previsoes_dict": {i: 0 for i in range(1, 13)}
            }
        
        mes = row['prev_mes']
        if mes is not None:
            produtos_dict[prod_id]["previsoes_dict"][mes] = row['prev_qtd']
            
    # Formata como lista estruturada para o frontend
    resultado = []
    for prod_id, info in produtos_dict.items():
        previsoes_lista = []
        for i in range(1, 13):
            previsoes_lista.append({
                "mes": meses_pt[i],
                "previsto": info["previsoes_dict"][i]
            })
            
        resultado.append({
            "produto": info["produto"],
            "categoria": info["categoria"],
            "previsoes": previsoes_lista
        })
        
    return jsonify(resultado)


if __name__ == '__main__':
    app.run(debug=True)
