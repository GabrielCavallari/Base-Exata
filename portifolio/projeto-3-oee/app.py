# Projeto 3 — Monitor de Eficiência Industrial OEE
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
        CREATE TABLE IF NOT EXISTS maquinas (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            setor TEXT NOT NULL,
            capacidade_hora INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS registros_turno (
            id INTEGER PRIMARY KEY,
            maquina_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            turno TEXT NOT NULL,
            tempo_planejado_min INTEGER NOT NULL,
            tempo_operando_min INTEGER NOT NULL,
            producao_total INTEGER NOT NULL,
            producao_aprovada INTEGER NOT NULL,
            FOREIGN KEY (maquina_id) REFERENCES maquinas(id)
        );

        CREATE TABLE IF NOT EXISTS demo_meta (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()


def banco_vazio():
    """Verifica se o banco está vazio (sem registros de turno)."""
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM registros_turno').fetchone()[0]
    conn.close()
    return total == 0


def inicializar_banco():
    """Cria tabelas e popula com dados de demonstração se necessário."""
    criar_tabelas()
    if banco_vazio():
        from seed_data import seed_database
        seed_database(DATABASE)


def atualizar_datas_demo():
    """Desloca datas de OEE demo para manter historico recente preenchido."""
    conn = sqlite3.connect(DATABASE)
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS demo_meta (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
        ''')
        row = conn.execute('SELECT MAX(data) FROM registros_turno').fetchone()
        max_data = row[0] if row else None
        if not max_data:
            conn.commit()
            return

        hoje = datetime.now().date()
        maior_data = datetime.strptime(max_data[:10], '%Y-%m-%d').date()
        dias = (hoje - maior_data).days

        if dias > 0:
            conn.execute("UPDATE registros_turno SET data = date(data, ?)", (f"+{dias} days",))

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


def format_pct(valor):
    return f"{float(valor or 0):.1f}%".replace(".", ",")


def classificar_oee(valor):
    if valor >= 75:
        return '<span class="badge badge-oee-bom">Bom</span>'
    if valor >= 60:
        return '<span class="badge badge-oee-atencao">Atenção</span>'
    return '<span class="badge badge-oee-critico">Crítico</span>'


def calcular_oee(registros):
    if not registros:
        return {'oee': 0, 'disp': 0, 'perf': 0, 'qual': 0, 'perda_min': 0, 'refugo': 0}

    soma_oee = soma_disp = soma_perf = soma_qual = 0
    perda_min = refugo = 0

    for r in registros:
        disp = r['tempo_operando_min'] / r['tempo_planejado_min'] if r['tempo_planejado_min'] else 0
        capacidade_ideal = r['capacidade_hora'] * (r['tempo_operando_min'] / 60)
        perf = r['producao_total'] / capacidade_ideal if capacidade_ideal else 0
        qual = r['producao_aprovada'] / r['producao_total'] if r['producao_total'] else 0
        soma_disp += disp
        soma_perf += perf
        soma_qual += qual
        soma_oee += disp * perf * qual
        perda_min += max(r['tempo_planejado_min'] - r['tempo_operando_min'], 0)
        refugo += max(r['producao_total'] - r['producao_aprovada'], 0)

    n = len(registros)
    return {
        'oee': soma_oee / n * 100,
        'disp': soma_disp / n * 100,
        'perf': soma_perf / n * 100,
        'qual': soma_qual / n * 100,
        'perda_min': perda_min,
        'refugo': refugo,
    }


def registros_oee():
    conn = get_db()
    rows = conn.execute('''
        SELECT rt.*, m.nome AS maquina, m.setor, m.capacidade_hora
        FROM registros_turno rt
        JOIN maquinas m ON m.id = rt.maquina_id
    ''').fetchall()
    conn.close()
    return rows


@app.route('/')
def dashboard():
    """Página principal do monitor de OEE."""
    return render_template('index.html')


@app.route('/maquinas')
def maquinas():
    registros = registros_oee()
    grupos = {}
    for row in registros:
        grupos.setdefault(row['maquina'], []).append(row)
    ranking = []
    for maquina, itens in grupos.items():
        metricas = calcular_oee(itens)
        ranking.append({'maquina': maquina, 'setor': itens[0]['setor'], 'registros': len(itens), **metricas})
    ranking.sort(key=lambda item: item['oee'], reverse=True)

    return render_template(
        'simple_page.html',
        title='Máquinas',
        icon='bi-cpu-fill',
        subtitle='Ranking de eficiência por equipamento',
        description='Visão para comparar máquinas, capacidade produtiva e eficiência média por equipamento.',
        kpis=[
            {'label': 'OEE médio', 'value': format_pct(sum(item['oee'] for item in ranking) / len(ranking) if ranking else 0), 'hint': 'Média das máquinas monitoradas.', 'icon': 'bi-speedometer2'},
            {'label': 'Máquina líder', 'value': ranking[0]['maquina'] if ranking else '-', 'hint': format_pct(ranking[0]['oee']) if ranking else 'Sem dados.', 'icon': 'bi-trophy'},
            {'label': 'Ponto crítico', 'value': ranking[-1]['maquina'] if ranking else '-', 'hint': format_pct(ranking[-1]['oee']) if ranking else 'Sem dados.', 'icon': 'bi-exclamation-triangle'},
            {'label': 'Equipamentos', 'value': len(ranking), 'hint': 'Máquinas com registros de turno.', 'icon': 'bi-cpu'},
        ],
        chart={
            'title': 'OEE médio por máquina',
            'type': 'bar',
            'suffix': '%',
            'labels': [item['maquina'] for item in ranking],
            'datasets': [{'label': 'OEE', 'data': [round(item['oee'], 1) for item in ranking], 'backgroundColor': '#008080'}]
        },
        insights=[
            {'title': 'Comparação objetiva', 'text': 'O ranking mostra rapidamente onde a produção performa bem e onde precisa de plano de ação.'},
            {'title': 'Conversa comercial', 'text': 'Ajuda a vender a ideia de acompanhamento por máquina sem depender de planilhas manuais.'},
        ],
        table={
            'title': 'Detalhe por máquina',
            'headers': ['Máquina', 'Setor', 'OEE', 'Disponib.', 'Performance', 'Qualidade', 'Status'],
            'rows': [[item['maquina'], item['setor'], format_pct(item['oee']), format_pct(item['disp']), format_pct(item['perf']), format_pct(item['qual']), classificar_oee(item['oee'])] for item in ranking]
        }
    )


@app.route('/turnos')
def turnos():
    registros = registros_oee()
    grupos = {}
    for row in registros:
        grupos.setdefault(row['turno'], []).append(row)
    ranking = []
    for turno, itens in grupos.items():
        metricas = calcular_oee(itens)
        ranking.append({'turno': turno, 'registros': len(itens), **metricas})
    ranking.sort(key=lambda item: item['turno'])

    return render_template(
        'simple_page.html',
        title='Turnos',
        icon='bi-clock-history',
        subtitle='Comparação operacional por turno',
        description='Área dedicada a analisar diferenças entre turnos, perdas recorrentes e oportunidades de ajuste operacional.',
        kpis=[
            {'label': 'Melhor turno', 'value': max(ranking, key=lambda item: item['oee'])['turno'] if ranking else '-', 'hint': format_pct(max(ranking, key=lambda item: item['oee'])['oee']) if ranking else 'Sem dados.', 'icon': 'bi-award'},
            {'label': 'Turno crítico', 'value': min(ranking, key=lambda item: item['oee'])['turno'] if ranking else '-', 'hint': format_pct(min(ranking, key=lambda item: item['oee'])['oee']) if ranking else 'Sem dados.', 'icon': 'bi-exclamation-circle'},
            {'label': 'Registros', 'value': sum(item['registros'] for item in ranking), 'hint': 'Amostras de produção analisadas.', 'icon': 'bi-clipboard-data'},
            {'label': 'Perda planejada', 'value': f"{sum(item['perda_min'] for item in ranking):,.0f} min".replace(",", "."), 'hint': 'Diferença entre tempo planejado e operando.', 'icon': 'bi-hourglass-split'},
        ],
        chart={
            'title': 'OEE, disponibilidade, performance e qualidade por turno',
            'type': 'bar',
            'suffix': '%',
            'labels': [f"Turno {item['turno']}" for item in ranking],
            'datasets': [
                {'label': 'OEE', 'data': [round(item['oee'], 1) for item in ranking], 'backgroundColor': '#1A365D'},
                {'label': 'Disponibilidade', 'data': [round(item['disp'], 1) for item in ranking], 'backgroundColor': '#008080'},
                {'label': 'Qualidade', 'data': [round(item['qual'], 1) for item in ranking], 'backgroundColor': '#D35400'},
            ]
        },
        insights=[
            {'title': 'Gestão de rotina', 'text': 'Turnos diferentes costumam esconder gargalos de setup, troca de equipe ou parada recorrente.'},
            {'title': 'Ação sugerida', 'text': 'Usar o melhor turno como referência operacional para treinar os demais.'},
        ],
        table={
            'title': 'Resumo por turno',
            'headers': ['Turno', 'Registros', 'OEE', 'Disponibilidade', 'Performance', 'Qualidade'],
            'rows': [[f"Turno {item['turno']}", item['registros'], format_pct(item['oee']), format_pct(item['disp']), format_pct(item['perf']), format_pct(item['qual'])] for item in ranking]
        }
    )


@app.route('/gargalos')
def gargalos():
    registros = registros_oee()
    grupos = {}
    for row in registros:
        chave = (row['maquina'], row['turno'])
        grupos.setdefault(chave, []).append(row)
    gargalos_lista = []
    for (maquina, turno), itens in grupos.items():
        metricas = calcular_oee(itens)
        gargalos_lista.append({'maquina': maquina, 'turno': turno, 'registros': len(itens), **metricas})
    gargalos_lista.sort(key=lambda item: item['oee'])
    criticos = [item for item in gargalos_lista if item['oee'] < 60]

    return render_template(
        'simple_page.html',
        title='Gargalos',
        icon='bi-exclamation-triangle-fill',
        subtitle='Pontos que mais derrubam a eficiência',
        description='Resumo para destacar máquinas, turnos ou indicadores que mais derrubam o OEE geral.',
        kpis=[
            {'label': 'Gargalos críticos', 'value': len(criticos), 'hint': 'Combinações máquina/turno abaixo de 60% OEE.', 'icon': 'bi-exclamation-octagon'},
            {'label': 'Maior perda', 'value': gargalos_lista[0]['maquina'] if gargalos_lista else '-', 'hint': f"Turno {gargalos_lista[0]['turno']} · {format_pct(gargalos_lista[0]['oee'])}" if gargalos_lista else 'Sem dados.', 'icon': 'bi-arrow-down-circle'},
            {'label': 'Minutos parados', 'value': f"{sum(item['perda_min'] for item in gargalos_lista):,.0f}".replace(",", "."), 'hint': 'Soma das perdas de disponibilidade.', 'icon': 'bi-stopwatch'},
            {'label': 'Refugo estimado', 'value': f"{sum(item['refugo'] for item in gargalos_lista):,.0f}".replace(",", "."), 'hint': 'Peças produzidas e não aprovadas.', 'icon': 'bi-trash3'},
        ],
        chart={
            'title': 'Menores OEEs por máquina e turno',
            'type': 'bar',
            'suffix': '%',
            'labels': [f"{item['maquina']} · {item['turno']}" for item in gargalos_lista[:8]],
            'datasets': [{'label': 'OEE', 'data': [round(item['oee'], 1) for item in gargalos_lista[:8]], 'backgroundColor': '#D35400'}]
        },
        insights=[
            {'title': 'Prioridade clara', 'text': 'A página evita discutir todas as máquinas ao mesmo tempo e foca nas maiores perdas.'},
            {'title': 'Recomendação', 'text': 'Investigar primeiro disponibilidade, depois performance e qualidade em cada gargalo.'},
        ],
        table={
            'title': 'Gargalos priorizados',
            'headers': ['Máquina', 'Turno', 'OEE', 'Perda min.', 'Refugo', 'Recomendação'],
            'rows': [[item['maquina'], f"Turno {item['turno']}", format_pct(item['oee']), f"{item['perda_min']:.0f}", f"{item['refugo']:.0f}", 'Plano de ação de disponibilidade' if item['disp'] < item['perf'] else 'Revisar cadência e qualidade'] for item in gargalos_lista[:12]]
        }
    )


@app.route('/relatorio-executivo')
def relatorio_executivo():
    registros = registros_oee()
    geral = calcular_oee(registros)
    grupos = {}
    for row in registros:
        grupos.setdefault(row['maquina'], []).append(row)
    ranking = [{'maquina': maquina, **calcular_oee(itens)} for maquina, itens in grupos.items()]
    ranking.sort(key=lambda item: item['oee'], reverse=True)

    return render_template(
        'simple_page.html',
        title='Relatório Executivo',
        icon='bi-file-earmark-bar-graph-fill',
        subtitle='Síntese gerencial de eficiência industrial',
        description='Síntese gerencial de eficiência, disponibilidade, performance, qualidade e próximos pontos de atenção.',
        kpis=[
            {'label': 'OEE geral', 'value': format_pct(geral['oee']), 'hint': 'Indicador consolidado da operação.', 'icon': 'bi-speedometer'},
            {'label': 'Disponibilidade', 'value': format_pct(geral['disp']), 'hint': 'Tempo operando sobre tempo planejado.', 'icon': 'bi-clock'},
            {'label': 'Performance', 'value': format_pct(geral['perf']), 'hint': 'Produção real frente à capacidade ideal.', 'icon': 'bi-activity'},
            {'label': 'Qualidade', 'value': format_pct(geral['qual']), 'hint': 'Produção aprovada sobre total produzido.', 'icon': 'bi-check2-circle'},
        ],
        chart={
            'title': 'Ranking executivo de máquinas',
            'type': 'bar',
            'suffix': '%',
            'labels': [item['maquina'] for item in ranking],
            'datasets': [{'label': 'OEE', 'data': [round(item['oee'], 1) for item in ranking], 'backgroundColor': '#1A365D'}]
        },
        insights=[
            {'title': 'Resumo para diretoria', 'text': 'A tela mostra se o problema principal está em tempo parado, cadência ou qualidade.'},
            {'title': 'Ação sugerida', 'text': 'Definir uma rotina semanal com ranking de máquinas e revisão dos três piores pontos.'},
        ],
        table={
            'title': 'Recomendações executivas',
            'headers': ['Prioridade', 'Máquina', 'Indicador', 'Ação sugerida'],
            'rows': [[idx + 1, item['maquina'], format_pct(item['oee']), 'Atacar disponibilidade' if item['disp'] < item['perf'] else 'Revisar cadência produtiva'] for idx, item in enumerate(reversed(ranking[-5:]))]
        }
    )


@app.route('/api/resumo')
def api_resumo():
    """API JSON: OEE geral e componentes (disponibilidade, performance, qualidade)."""
    conn = get_db()

    registros = conn.execute('''
        SELECT
            rt.tempo_planejado_min,
            rt.tempo_operando_min,
            rt.producao_total,
            rt.producao_aprovada,
            m.capacidade_hora
        FROM registros_turno rt
        JOIN maquinas m ON m.id = rt.maquina_id
    ''').fetchall()

    conn.close()

    if not registros:
        return jsonify({
            'oee_geral': 0.0,
            'disponibilidade': 0.0,
            'performance': 0.0,
            'qualidade': 0.0
        })

    soma_disp = soma_perf = soma_qual = soma_oee = 0.0

    for r in registros:
        disp = r['tempo_operando_min'] / r['tempo_planejado_min'] if r['tempo_planejado_min'] > 0 else 0.0
        capacidade_ideal = r['capacidade_hora'] * (r['tempo_operando_min'] / 60)
        perf = r['producao_total'] / capacidade_ideal if capacidade_ideal > 0 else 0.0
        qual = r['producao_aprovada'] / r['producao_total'] if r['producao_total'] > 0 else 0.0
        oee = disp * perf * qual

        soma_disp += disp
        soma_perf += perf
        soma_qual += qual
        soma_oee += oee

    n = len(registros)

    return jsonify({
        'oee_geral': round(soma_oee / n, 4),
        'disponibilidade': round(soma_disp / n, 4),
        'performance': round(soma_perf / n, 4),
        'qualidade': round(soma_qual / n, 4)
    })


@app.route('/api/oee-por-maquina')
def api_oee_por_maquina():
    """API JSON: OEE médio por máquina, ordenado do maior para o menor."""
    conn = get_db()

    maquinas = conn.execute('SELECT id, nome FROM maquinas ORDER BY nome').fetchall()

    resultado = []

    for maquina in maquinas:
        registros = conn.execute('''
            SELECT
                rt.tempo_planejado_min,
                rt.tempo_operando_min,
                rt.producao_total,
                rt.producao_aprovada,
                m.capacidade_hora
            FROM registros_turno rt
            JOIN maquinas m ON m.id = rt.maquina_id
            WHERE rt.maquina_id = ?
        ''', (maquina['id'],)).fetchall()

        if not registros:
            continue

        soma_disp = soma_perf = soma_qual = soma_oee = 0.0

        for r in registros:
            disp = r['tempo_operando_min'] / r['tempo_planejado_min'] if r['tempo_planejado_min'] > 0 else 0.0
            capacidade_ideal = r['capacidade_hora'] * (r['tempo_operando_min'] / 60)
            perf = r['producao_total'] / capacidade_ideal if capacidade_ideal > 0 else 0.0
            qual = r['producao_aprovada'] / r['producao_total'] if r['producao_total'] > 0 else 0.0
            oee = disp * perf * qual

            soma_disp += disp
            soma_perf += perf
            soma_qual += qual
            soma_oee += oee

        n = len(registros)

        resultado.append({
            'nome': maquina['nome'],
            'oee': round(soma_oee / n, 4),
            'disponibilidade': round(soma_disp / n, 4),
            'performance': round(soma_perf / n, 4),
            'qualidade': round(soma_qual / n, 4)
        })

    conn.close()

    resultado.sort(key=lambda x: x['oee'], reverse=True)

    return jsonify(resultado)


@app.route('/api/oee-historico')
def api_oee_historico():
    """API JSON: OEE médio diário dos últimos 30 dias, do mais antigo ao mais recente."""
    conn = get_db()

    hoje = datetime.now().date()
    resultado = []

    for i in range(29, -1, -1):
        data = hoje - timedelta(days=i)
        data_str = data.strftime('%Y-%m-%d')

        registros = conn.execute('''
            SELECT
                rt.tempo_planejado_min,
                rt.tempo_operando_min,
                rt.producao_total,
                rt.producao_aprovada,
                m.capacidade_hora
            FROM registros_turno rt
            JOIN maquinas m ON m.id = rt.maquina_id
            WHERE rt.data = ?
        ''', (data_str,)).fetchall()

        if not registros:
            continue

        soma_oee = 0.0

        for r in registros:
            disp = r['tempo_operando_min'] / r['tempo_planejado_min'] if r['tempo_planejado_min'] > 0 else 0.0
            capacidade_ideal = r['capacidade_hora'] * (r['tempo_operando_min'] / 60)
            perf = r['producao_total'] / capacidade_ideal if capacidade_ideal > 0 else 0.0
            qual = r['producao_aprovada'] / r['producao_total'] if r['producao_total'] > 0 else 0.0
            soma_oee += disp * perf * qual

        resultado.append({
            'data': data.strftime('%d/%m'),
            'oee': round(soma_oee / len(registros), 4)
        })

    conn.close()

    return jsonify(resultado)


@app.route('/api/heatmap')
def api_heatmap():
    """API JSON: OEE médio por máquina por turno (A, B, C), ordenado por nome."""
    conn = get_db()

    maquinas = conn.execute('SELECT id, nome FROM maquinas ORDER BY nome').fetchall()

    resultado = []

    for maquina in maquinas:
        entrada = {'maquina': maquina['nome'], 'turno_a': None, 'turno_b': None, 'turno_c': None}

        for turno, campo in [('A', 'turno_a'), ('B', 'turno_b'), ('C', 'turno_c')]:
            registros = conn.execute('''
                SELECT
                    rt.tempo_planejado_min,
                    rt.tempo_operando_min,
                    rt.producao_total,
                    rt.producao_aprovada,
                    m.capacidade_hora
                FROM registros_turno rt
                JOIN maquinas m ON m.id = rt.maquina_id
                WHERE rt.maquina_id = ? AND rt.turno = ?
            ''', (maquina['id'], turno)).fetchall()

            if not registros:
                continue

            soma_oee = 0.0

            for r in registros:
                disp = r['tempo_operando_min'] / r['tempo_planejado_min'] if r['tempo_planejado_min'] > 0 else 0.0
                capacidade_ideal = r['capacidade_hora'] * (r['tempo_operando_min'] / 60)
                perf = r['producao_total'] / capacidade_ideal if capacidade_ideal > 0 else 0.0
                qual = r['producao_aprovada'] / r['producao_total'] if r['producao_total'] > 0 else 0.0
                soma_oee += disp * perf * qual

            entrada[campo] = round(soma_oee / len(registros), 4)

        resultado.append(entrada)

    conn.close()

    return jsonify(resultado)


if __name__ == '__main__':
    app.run(debug=True)
