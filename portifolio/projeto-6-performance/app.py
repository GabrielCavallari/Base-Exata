# Projeto 6 — Painel de Performance Comercial
# Base Exata | Flask + SQLite

import sqlite3
import os
from datetime import datetime, date, timedelta
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Caminho absoluto para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')


def get_db():
    """Retorna uma conexão ativa com o banco SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.row_factory = sqlite3.Row
    return conn


def criar_tabelas():
    """Cria as tabelas do banco de dados caso não existam."""
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS vendedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            regiao TEXT NOT NULL,
            meta_mensal REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendedor_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            valor REAL NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Concluída', 'Cancelada')),
            FOREIGN KEY (vendedor_id) REFERENCES vendedores(id)
        );

        CREATE TABLE IF NOT EXISTS demo_meta (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()


def banco_vazio():
    """Verifica se o banco de dados de vendedores está vazio."""
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM vendedores').fetchone()[0]
    conn.close()
    return total == 0


def inicializar_banco():
    """Inicializa as tabelas e roda o script de seed caso o banco esteja vazio."""
    criar_tabelas()
    if banco_vazio():
        from seed_data import popular_banco
        popular_banco(DATABASE)


def atualizar_datas_demo():
    """Desloca datas de vendas demo para manter o mes atual preenchido."""
    conn = sqlite3.connect(DATABASE)
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS demo_meta (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
        ''')
        row = conn.execute('SELECT MAX(data) FROM vendas').fetchone()
        max_data = row[0] if row else None
        if not max_data:
            conn.commit()
            return

        hoje = date.today()
        maior_data = datetime.strptime(max_data[:10], '%Y-%m-%d').date()
        dias = (hoje - maior_data).days

        if dias > 0:
            conn.execute("UPDATE vendas SET data = date(data, ?)", (f"+{dias} days",))

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


# Inicializa banco de dados na importação do módulo
inicializar_banco()
atualizar_datas_demo()


@app.before_request
def refresh_demo_dates_once_per_day():
    hoje = date.today().strftime('%Y-%m-%d')
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


def badge_meta(percentual):
    if percentual >= 100:
        return '<span class="badge badge-status badge-status-success">Meta batida</span>'
    if percentual >= 85:
        return '<span class="badge badge-status badge-status-warning">Próximo da meta</span>'
    return '<span class="badge badge-status badge-status-danger">Ação necessária</span>'


@app.route('/')
def dashboard():
    """Renderiza a página principal do Painel de Performance Comercial."""
    return render_template('index.html')


@app.route('/vendedores')
def vendedores():
    conn = get_db()
    rows = conn.execute('''
        SELECT v.id, v.nome, v.regiao, v.meta_mensal,
               SUM(CASE WHEN s.status = 'Concluída' THEN s.valor ELSE 0 END) AS realizado,
               COUNT(s.id) AS oportunidades,
               SUM(CASE WHEN s.status = 'Concluída' THEN 1 ELSE 0 END) AS concluidas
        FROM vendedores v
        LEFT JOIN vendas s ON s.vendedor_id = v.id
        GROUP BY v.id, v.nome, v.regiao, v.meta_mensal
        ORDER BY realizado DESC
    ''').fetchall()
    conn.close()

    return render_template(
        'simple_page.html',
        title='Vendedores',
        icon='bi-people-fill',
        subtitle='Ranking comercial por vendedor',
        description='Visão para comparar vendedores, ranking, conversão e distância individual para a meta.',
        kpis=[
            {'label': 'Líder comercial', 'value': rows[0]['nome'] if rows else '-', 'hint': format_brl(rows[0]['realizado']) if rows else 'Sem dados.', 'icon': 'bi-trophy'},
            {'label': 'Vendedores', 'value': len(rows), 'hint': 'Equipe cadastrada na demo.', 'icon': 'bi-people'},
            {'label': 'Conversão média', 'value': format_pct(sum((row['concluidas'] / row['oportunidades'] * 100) if row['oportunidades'] else 0 for row in rows) / len(rows) if rows else 0), 'hint': 'Média das taxas individuais.', 'icon': 'bi-check2-circle'},
            {'label': 'Realizado total', 'value': format_brl(sum(row['realizado'] or 0 for row in rows)), 'hint': 'Somente vendas concluídas.', 'icon': 'bi-cash-stack'},
        ],
        chart={
            'title': 'Faturamento por vendedor',
            'type': 'bar',
            'prefix': 'R$ ',
            'labels': [row['nome'] for row in rows],
            'datasets': [{'label': 'Realizado', 'data': [round(row['realizado'] or 0, 2) for row in rows], 'backgroundColor': '#10b981'}]
        },
        insights=[
            {'title': 'Gestão de equipe', 'text': 'O ranking torna visível quem puxa o resultado e quem precisa de acompanhamento.'},
            {'title': 'Ação sugerida', 'text': 'Usar a taxa de conversão para separar problema de volume de oportunidades de problema de fechamento.'},
        ],
        table={
            'title': 'Desempenho individual',
            'headers': ['Vendedor', 'Região', 'Realizado', 'Meta 6 meses', 'Conversão', 'Status'],
            'rows': [[row['nome'], row['regiao'], format_brl(row['realizado']), format_brl(row['meta_mensal'] * 6), format_pct((row['concluidas'] / row['oportunidades'] * 100) if row['oportunidades'] else 0), badge_meta((row['realizado'] / (row['meta_mensal'] * 6) * 100) if row['meta_mensal'] else 0)] for row in rows]
        }
    )


@app.route('/regioes')
def regioes():
    conn = get_db()
    rows = conn.execute('''
        SELECT v.regiao,
               COUNT(DISTINCT v.id) AS vendedores,
               SUM(CASE WHEN s.status = 'Concluída' THEN s.valor ELSE 0 END) AS realizado,
               SUM(v.meta_mensal) * 6 AS meta,
               COUNT(s.id) AS oportunidades
        FROM vendedores v
        LEFT JOIN vendas s ON s.vendedor_id = v.id
        GROUP BY v.regiao
        ORDER BY realizado DESC
    ''').fetchall()
    conn.close()

    return render_template(
        'simple_page.html',
        title='Regiões',
        icon='bi-geo-alt-fill',
        subtitle='Desempenho comercial por região',
        description='Área para analisar faturamento por região, concentração comercial e oportunidades de redistribuição de foco.',
        kpis=[
            {'label': 'Região líder', 'value': rows[0]['regiao'] if rows else '-', 'hint': format_brl(rows[0]['realizado']) if rows else 'Sem dados.', 'icon': 'bi-geo-alt'},
            {'label': 'Regiões', 'value': len(rows), 'hint': 'Praças atendidas pela equipe.', 'icon': 'bi-map'},
            {'label': 'Cobertura total', 'value': sum(row['vendedores'] for row in rows), 'hint': 'Vendedores distribuídos nas regiões.', 'icon': 'bi-person-lines-fill'},
            {'label': 'Oportunidades', 'value': sum(row['oportunidades'] or 0 for row in rows), 'hint': 'Vendas concluídas e canceladas.', 'icon': 'bi-bullseye'},
        ],
        chart={
            'title': 'Realizado por região',
            'type': 'doughnut',
            'prefix': 'R$ ',
            'labels': [row['regiao'] for row in rows],
            'datasets': [{'label': 'Realizado', 'data': [round(row['realizado'] or 0, 2) for row in rows], 'backgroundColor': ['#10b981', '#0f172a', '#0ea5e9', '#f59e0b', '#f43f5e', '#64748b']}]
        },
        insights=[
            {'title': 'Território visível', 'text': 'A tela ajuda a discutir expansão, foco de visitas e distribuição de carteira.'},
            {'title': 'Ação sugerida', 'text': 'Regiões abaixo da meta podem receber reforço de carteira ou campanhas específicas.'},
        ],
        table={
            'title': 'Regiões e metas',
            'headers': ['Região', 'Vendedores', 'Realizado', 'Meta 6 meses', 'Atingimento'],
            'rows': [[row['regiao'], row['vendedores'], format_brl(row['realizado']), format_brl(row['meta']), format_pct((row['realizado'] / row['meta'] * 100) if row['meta'] else 0)] for row in rows]
        }
    )


@app.route('/metas')
def metas():
    hoje = date.today()
    meses = []
    meses_nomes_pt = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    for i in range(5, -1, -1):
        ano = hoje.year
        mes = hoje.month - i
        while mes <= 0:
            mes += 12
            ano -= 1
        meses.append({'mes_ano': f"{ano}-{mes:02d}", 'label': f"{meses_nomes_pt[mes]}/{str(ano)[2:]}"})

    conn = get_db()
    meta_mensal = conn.execute('SELECT COALESCE(SUM(meta_mensal), 0) FROM vendedores').fetchone()[0]
    rows = []
    for item in meses:
        realizado = conn.execute('''
            SELECT COALESCE(SUM(valor), 0)
            FROM vendas
            WHERE status = 'Concluída' AND strftime('%Y-%m', data) = ?
        ''', (item['mes_ano'],)).fetchone()[0]
        rows.append({'mes': item['label'], 'realizado': realizado, 'meta': meta_mensal, 'atingimento': (realizado / meta_mensal * 100) if meta_mensal else 0})
    conn.close()

    return render_template(
        'simple_page.html',
        title='Metas',
        icon='bi-bullseye',
        subtitle='Realizado versus meta mensal',
        description='Resumo para acompanhar metas mensais, atingimento acumulado e desvios que exigem ação do gestor.',
        kpis=[
            {'label': 'Meta mensal global', 'value': format_brl(meta_mensal), 'hint': 'Soma das metas dos vendedores.', 'icon': 'bi-bullseye'},
            {'label': 'Realizado no mês', 'value': format_brl(rows[-1]['realizado'] if rows else 0), 'hint': rows[-1]['mes'] if rows else 'Sem dados.', 'icon': 'bi-calendar-check'},
            {'label': 'Atingimento atual', 'value': format_pct(rows[-1]['atingimento'] if rows else 0), 'hint': 'Realizado dividido pela meta mensal.', 'icon': 'bi-percent'},
            {'label': 'Meses na análise', 'value': len(rows), 'hint': 'Janela comercial recente.', 'icon': 'bi-calendar3'},
        ],
        chart={
            'title': 'Evolução de metas',
            'type': 'bar',
            'prefix': 'R$ ',
            'labels': [row['mes'] for row in rows],
            'datasets': [
                {'label': 'Realizado', 'data': [round(row['realizado'] or 0, 2) for row in rows], 'backgroundColor': '#10b981'},
                {'label': 'Meta', 'data': [round(row['meta'] or 0, 2) for row in rows], 'backgroundColor': '#0f172a'},
            ]
        },
        insights=[
            {'title': 'Controle de desvio', 'text': 'A página deixa explícito quando o mês exige reforço comercial antes do fechamento.'},
            {'title': 'Ação sugerida', 'text': 'Quando o realizado ficar abaixo de 85%, revisar carteira ativa e oportunidades em aberto.'},
        ],
        table={
            'title': 'Acompanhamento mensal',
            'headers': ['Mês', 'Realizado', 'Meta', 'Atingimento', 'Status'],
            'rows': [[row['mes'], format_brl(row['realizado']), format_brl(row['meta']), format_pct(row['atingimento']), badge_meta(row['atingimento'])] for row in rows]
        }
    )


@app.route('/relatorio-executivo')
def relatorio_executivo():
    conn = get_db()
    vendedores_rows = conn.execute('''
        SELECT v.nome, v.regiao, v.meta_mensal,
               SUM(CASE WHEN s.status = 'Concluída' THEN s.valor ELSE 0 END) AS realizado,
               COUNT(s.id) AS oportunidades,
               SUM(CASE WHEN s.status = 'Concluída' THEN 1 ELSE 0 END) AS concluidas
        FROM vendedores v
        LEFT JOIN vendas s ON s.vendedor_id = v.id
        GROUP BY v.id, v.nome, v.regiao, v.meta_mensal
        ORDER BY realizado DESC
    ''').fetchall()
    regioes_rows = conn.execute('''
        SELECT v.regiao, SUM(CASE WHEN s.status = 'Concluída' THEN s.valor ELSE 0 END) AS realizado
        FROM vendedores v
        LEFT JOIN vendas s ON s.vendedor_id = v.id
        GROUP BY v.regiao
        ORDER BY realizado DESC
    ''').fetchall()
    conn.close()
    realizado_total = sum(row['realizado'] or 0 for row in vendedores_rows)
    meta_total = sum((row['meta_mensal'] or 0) * 6 for row in vendedores_rows)
    taxa_media = sum((row['concluidas'] / row['oportunidades'] * 100) if row['oportunidades'] else 0 for row in vendedores_rows) / len(vendedores_rows) if vendedores_rows else 0

    return render_template(
        'simple_page.html',
        title='Relatório Executivo',
        icon='bi-file-earmark-bar-graph-fill',
        subtitle='Resumo comercial para ação gerencial',
        description='Síntese comercial com faturamento, regiões, ranking de vendedores e metas para decisão gerencial.',
        kpis=[
            {'label': 'Realizado total', 'value': format_brl(realizado_total), 'hint': 'Vendas concluídas no histórico demo.', 'icon': 'bi-cash-stack'},
            {'label': 'Atingimento global', 'value': format_pct((realizado_total / meta_total * 100) if meta_total else 0), 'hint': 'Realizado contra meta acumulada.', 'icon': 'bi-bullseye'},
            {'label': 'Conversão média', 'value': format_pct(taxa_media), 'hint': 'Média de fechamento por vendedor.', 'icon': 'bi-check2-circle'},
            {'label': 'Região líder', 'value': regioes_rows[0]['regiao'] if regioes_rows else '-', 'hint': format_brl(regioes_rows[0]['realizado']) if regioes_rows else 'Sem dados.', 'icon': 'bi-geo-alt'},
        ],
        chart={
            'title': 'Ranking executivo de vendedores',
            'type': 'bar',
            'prefix': 'R$ ',
            'labels': [row['nome'] for row in vendedores_rows],
            'datasets': [{'label': 'Realizado', 'data': [round(row['realizado'] or 0, 2) for row in vendedores_rows], 'backgroundColor': '#10b981'}]
        },
        insights=[
            {'title': 'Mensagem executiva', 'text': 'A página combina resultado, meta e concentração regional em uma leitura única.'},
            {'title': 'Ações sugeridas', 'text': 'Reforçar regiões abaixo da meta, replicar práticas dos líderes e revisar carteira inativa.'},
        ],
        table={
            'title': 'Plano de ação comercial',
            'headers': ['Prioridade', 'Vendedor', 'Região', 'Atingimento', 'Ação sugerida'],
            'rows': [[idx + 1, row['nome'], row['regiao'], format_pct((row['realizado'] / (row['meta_mensal'] * 6) * 100) if row['meta_mensal'] else 0), 'Manter ritmo e replicar abordagem' if idx < 2 else 'Revisar funil e carteira ativa'] for idx, row in enumerate(vendedores_rows)]
        }
    )


@app.route('/api/resumo')
def api_resumo():
    """API JSON: Retorna os 4 KPIs principais superiores."""
    conn = get_db()
    
    # 1. Faturamento Total (Apenas vendas Concluídas)
    faturamento_total = conn.execute('''
        SELECT COALESCE(SUM(valor), 0) FROM vendas WHERE status = 'Concluída'
    ''').fetchone()[0]
    
    # 2. Taxa de Conversão (vendas concluídas / total)
    total_vendas = conn.execute('SELECT COUNT(*) FROM vendas').fetchone()[0]
    if total_vendas > 0:
        concluidas = conn.execute('''
            SELECT COUNT(*) FROM vendas WHERE status = 'Concluída'
        ''').fetchone()[0]
        taxa_conversao = (concluidas / total_vendas) * 100
    else:
        taxa_conversao = 0.0

    # 3. Melhor Vendedor do Mês Atual
    mes_atual = date.today().strftime('%Y-%m')
    row_lider = conn.execute('''
        SELECT v.nome, COALESCE(SUM(s.valor), 0) as total
        FROM vendas s
        JOIN vendedores v ON s.vendedor_id = v.id
        WHERE s.status = 'Concluída' AND strftime('%Y-%m', s.data) = ?
        GROUP BY v.id, v.nome
        ORDER BY total DESC
        LIMIT 1
    ''', (mes_atual,)).fetchone()
    
    # Fallback caso o mês atual não tenha vendas (ex: início do mês)
    if not row_lider:
        row_lider = conn.execute('''
            SELECT v.nome, COALESCE(SUM(s.valor), 0) as total
            FROM vendas s
            JOIN vendedores v ON s.vendedor_id = v.id
            WHERE s.status = 'Concluída'
            GROUP BY v.id, v.nome
            ORDER BY total DESC
            LIMIT 1
        ''').fetchone()
        
    melhor_vendedor = row_lider['nome'] if row_lider else "Nenhum"
    faturamento_lider = row_lider['total'] if row_lider else 0.0

    # 4. % de atingimento da meta global (últimos 6 meses)
    # Meta global = (Soma das metas mensais de todos os vendedores) * 6 meses
    soma_metas_mensais = conn.execute('SELECT COALESCE(SUM(meta_mensal), 0) FROM vendedores').fetchone()[0]
    meta_global = soma_metas_mensais * 6
    
    atingimento_global = (faturamento_total / meta_global * 100) if meta_global > 0 else 0.0

    conn.close()

    return jsonify({
        'faturamento_total': round(faturamento_total, 2),
        'taxa_conversao': round(taxa_conversao, 1),
        'melhor_vendedor': melhor_vendedor,
        'faturamento_lider': round(faturamento_lider, 2),
        'atingimento_global': round(atingimento_global, 1)
    })


@app.route('/api/ranking-vendedores')
def api_ranking_vendedores():
    """API JSON: Retorna o ranking dos vendedores ordenados pelo total de faturamento."""
    conn = get_db()
    
    rows = conn.execute('''
        SELECT v.id, v.nome, v.regiao, v.meta_mensal,
               COALESCE(SUM(CASE WHEN s.status = 'Concluída' THEN s.valor ELSE 0 END), 0) as total_faturado
        FROM vendedores v
        LEFT JOIN vendas s ON s.vendedor_id = v.id
        GROUP BY v.id, v.nome, v.regiao, v.meta_mensal
        ORDER BY total_faturado DESC
    ''').fetchall()
    
    conn.close()

    resultado = []
    for row in rows:
        meta_total_6meses = row['meta_mensal'] * 6
        total_faturado = row['total_faturado']
        
        percentual = (total_faturado / meta_total_6meses * 100) if meta_total_6meses > 0 else 0.0
        
        resultado.append({
            'id': row['id'],
            'nome': row['nome'],
            'regiao': row['regiao'],
            'meta_mensal': round(row['meta_mensal'], 2),
            'meta_total_6meses': round(meta_total_6meses, 2),
            'total_faturado': round(total_faturado, 2),
            'percentual_atingimento': round(percentual, 1)
        })

    return jsonify(resultado)


@app.route('/api/vendas-regiao')
def api_vendas_regiao():
    """API JSON: Retorna o faturamento concluído agrupado por região."""
    conn = get_db()
    
    rows = conn.execute('''
        SELECT v.regiao,
               COALESCE(SUM(CASE WHEN s.status = 'Concluída' THEN s.valor ELSE 0 END), 0) as total
        FROM vendedores v
        LEFT JOIN vendas s ON s.vendedor_id = v.id
        GROUP BY v.regiao
        ORDER BY total DESC
    ''').fetchall()
    
    conn.close()

    resultado = []
    for row in rows:
        resultado.append({
            'regiao': row['regiao'],
            'total': round(row['total'], 2)
        })

    return jsonify(resultado)


@app.route('/api/evolucao-metas')
def api_evolucao_metas():
    """API JSON: Comparativo mensal de Vendas Realizadas vs. Meta Esperada nos últimos 6 meses."""
    # Obter os últimos 6 meses retroativos
    hoje = date.today()
    meses = []
    
    for i in range(5, -1, -1):
        ano = hoje.year
        mes = hoje.month - i
        while mes <= 0:
            mes += 12
            ano -= 1
        
        mes_str = f"{ano}-{mes:02d}"
        
        meses_nomes_pt = {
            1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
        }
        
        label = f"{meses_nomes_pt[mes]}/{str(ano)[2:]}"
        meses.append({
            'mes_ano': mes_str,
            'label': label
        })

    conn = get_db()
    
    # Meta mensal global esperada é a soma de todas as metas dos vendedores
    meta_mensal_global = conn.execute('SELECT COALESCE(SUM(meta_mensal), 0) FROM vendedores').fetchone()[0]
    
    resultado = []
    for m in meses:
        realizado = conn.execute('''
            SELECT COALESCE(SUM(valor), 0)
            FROM vendas
            WHERE status = 'Concluída' AND strftime('%Y-%m', data) = ?
        ''', (m['mes_ano'],)).fetchone()[0]
        
        resultado.append({
            'mes': m['label'],
            'realizado': round(realizado, 2),
            'meta': round(meta_mensal_global, 2)
        })
        
    conn.close()
    
    return jsonify(resultado)


if __name__ == '__main__':
    app.run(debug=True)
