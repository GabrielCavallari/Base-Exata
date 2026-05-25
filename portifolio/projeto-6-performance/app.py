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


# Inicializa banco de dados na importação do módulo
inicializar_banco()


@app.route('/')
def dashboard():
    """Renderiza a página principal do Painel de Performance Comercial."""
    return render_template('index.html')


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
