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


# Inicializa o banco de dados no nível do módulo
inicializar_banco()


@app.context_processor
def inject_now():
    return {'data_atual': datetime.now().strftime('%d/%m/%Y')}


@app.route('/')
def index():
    """Renderiza a página principal do dashboard de sazonalidade."""
    return render_template('index.html')


@app.route('/produtos')
def produtos():
    return render_template(
        'simple_page.html',
        title='Produtos',
        icon='bi-box-seam-fill',
        description='Visão preparada para analisar itens com maior giro, categorias sazonais e produtos que exigem planejamento de compra.'
    )


@app.route('/previsao-demanda')
def previsao_demanda():
    return render_template(
        'simple_page.html',
        title='Previsão de Demanda',
        icon='bi-graph-up-arrow',
        description='Área para detalhar demanda prevista por produto, mês e categoria antes de decisões de compra.'
    )


@app.route('/sazonalidade-mensal')
def sazonalidade_mensal():
    return render_template(
        'simple_page.html',
        title='Sazonalidade Mensal',
        icon='bi-calendar-month-fill',
        description='Resumo para comparar meses de pico, meses fracos e padrões recorrentes de venda.'
    )


@app.route('/relatorio-executivo')
def relatorio_executivo():
    return render_template(
        'simple_page.html',
        title='Relatório Executivo',
        icon='bi-file-earmark-bar-graph-fill',
        description='Síntese gerencial para orientar compras, estoque e campanhas conforme a previsão de demanda.'
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
