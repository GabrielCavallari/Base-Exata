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


@app.route('/')
def dashboard():
    """Página principal do monitor de OEE."""
    return render_template('index.html')


@app.route('/maquinas')
def maquinas():
    return render_template(
        'simple_page.html',
        title='Máquinas',
        icon='bi-cpu-fill',
        description='Visão preparada para comparar máquinas, capacidade produtiva e eficiência média por equipamento.'
    )


@app.route('/turnos')
def turnos():
    return render_template(
        'simple_page.html',
        title='Turnos',
        icon='bi-clock-history',
        description='Área dedicada a analisar diferenças entre turnos, perdas recorrentes e oportunidades de ajuste operacional.'
    )


@app.route('/gargalos')
def gargalos():
    return render_template(
        'simple_page.html',
        title='Gargalos',
        icon='bi-exclamation-triangle-fill',
        description='Resumo para destacar máquinas, turnos ou indicadores que mais derrubam o OEE geral.'
    )


@app.route('/relatorio-executivo')
def relatorio_executivo():
    return render_template(
        'simple_page.html',
        title='Relatório Executivo',
        icon='bi-file-earmark-bar-graph-fill',
        description='Síntese gerencial de eficiência, disponibilidade, performance, qualidade e próximos pontos de atenção.'
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
