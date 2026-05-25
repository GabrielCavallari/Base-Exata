# Seed de dados para demonstração — Projeto 4 Automação de Relatórios
# Base Exata | Dados simulados de supermercado em Capivari, SP

import sqlite3
import random
from datetime import date, timedelta


def seed_database(database_path):
    """Popula o banco com categorias, fornecedores, vendas e ticket diário dos últimos 12 meses."""
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # 8 categorias com margem média realista para varejo de interior SP
    # (nome, margem_media)
    categorias = [
        ('Hortifruti',      0.35),
        ('Bebidas',         0.28),
        ('Padaria',         0.42),
        ('Carnes e Aves',   0.22),
        ('Laticínios',      0.30),
        ('Higiene Pessoal', 0.38),
        ('Limpeza',         0.32),
        ('Mercearia',       0.25),
    ]

    cursor.executemany(
        'INSERT INTO categorias (nome, margem_media) VALUES (?, ?)',
        categorias
    )
    conn.commit()

    # Busca IDs das categorias inseridas pelo nome
    rows_cat = cursor.execute('SELECT id, nome FROM categorias').fetchall()
    cat_ids = {nome: id_ for id_, nome in rows_cat}

    # 20 fornecedores distribuídos entre as 8 categorias (2-3 por categoria)
    # (nome, cidade, categoria_nome)
    fornecedores = [
        # Hortifruti
        ('Sítio São Benedito',             'Capivari',                'Hortifruti'),
        ('Hortifruti Capivari Ltda',       'Capivari',                'Hortifruti'),
        # Bebidas
        ('Distribuidora Paulista de Bebidas', 'Piracicaba',           'Bebidas'),
        ('Atacadão Bebidas Piracicaba',    'Piracicaba',              'Bebidas'),
        ('Cooperativa Tietê',              'Capivari',                'Bebidas'),
        # Padaria
        ('Moinho Central Ltda',            'Campinas',                'Padaria'),
        ('Padaria Industrial Campinas',    'Campinas',                'Padaria'),
        # Carnes e Aves
        ('Frigorífico Vale do Tietê',      'Capivari',                'Carnes e Aves'),
        ('Abatedouro São João da Boa Vista', 'São João da Boa Vista', 'Carnes e Aves'),
        ('Aves do Interior',               'Rio Claro',               'Carnes e Aves'),
        # Laticínios
        ('Laticínios Bela Vista',          'Piracicaba',              'Laticínios'),
        ('Cooperativa Leite Capivari',     'Capivari',                'Laticínios'),
        # Higiene Pessoal
        ('Distribuidora Higiene SP',       'Sorocaba',                'Higiene Pessoal'),
        ('Atacado Casa Limpa',             'Campinas',                'Higiene Pessoal'),
        # Limpeza
        ('Produtos Limpeza Sorocaba',      'Sorocaba',                'Limpeza'),
        ('Distribuidora Lar Ltda',         'Campinas',                'Limpeza'),
        # Mercearia
        ('Atacadão Mercearia SP',          'Campinas',                'Mercearia'),
        ('Distribuidora Central Interior', 'Rio Claro',               'Mercearia'),
        ('Grãos e Cereais Ltda',           'Piracicaba',              'Mercearia'),
        # Extra Hortifruti para fechar 20
        ('Verde Campo Distribuidora',      'Rio Claro',               'Hortifruti'),
    ]

    cursor.executemany(
        'INSERT INTO fornecedores (nome, cidade, categoria_id) VALUES (?, ?, ?)',
        [(nome, cidade, cat_ids[cat_nome]) for nome, cidade, cat_nome in fornecedores]
    )
    conn.commit()

    # Busca IDs dos fornecedores agrupados por categoria
    rows_forn = cursor.execute(
        'SELECT id, categoria_id FROM fornecedores'
    ).fetchall()

    # Dicionário: categoria_id → lista de fornecedor_ids
    forn_por_cat = {}
    for forn_id, cat_id in rows_forn:
        forn_por_cat.setdefault(cat_id, []).append(forn_id)

    # Todos os fornecedor_ids para seleção aleatória
    todos_forn = [forn_id for forn_id, _ in rows_forn]

    # Top 3 fornecedores que terão volume 2x maior (forçar destaque no ranking)
    top_forn_ids = [
        cat_ids['Bebidas'],        # substitui abaixo por forn_ids reais
    ]
    # Pega os primeiros fornecedores das categorias com maior volume esperado
    top_3_forn = (
        forn_por_cat[cat_ids['Bebidas']][:1] +
        forn_por_cat[cat_ids['Mercearia']][:1] +
        forn_por_cat[cat_ids['Carnes e Aves']][:1]
    )

    # Limites de valor_total por categoria para maior realismo
    # Bebidas e Mercearia têm volumes maiores, Hortifruti e Padaria menores
    limites_categoria = {
        cat_ids['Hortifruti']:      (200.0, 3000.0),
        cat_ids['Bebidas']:         (500.0, 8000.0),
        cat_ids['Padaria']:         (200.0, 3000.0),
        cat_ids['Carnes e Aves']:   (400.0, 6000.0),
        cat_ids['Laticínios']:      (300.0, 5000.0),
        cat_ids['Higiene Pessoal']: (300.0, 4500.0),
        cat_ids['Limpeza']:         (250.0, 4000.0),
        cat_ids['Mercearia']:       (500.0, 8000.0),
    }

    todos_cat_ids = list(cat_ids.values())

    # Gera vendas para cada dia dos últimos 12 meses
    hoje = date.today()
    data_inicio = hoje - timedelta(days=365)

    vendas = []
    data_atual = data_inicio

    while data_atual <= hoje:
        data_str = data_atual.strftime('%Y-%m-%d')

        # Entre 4 e 8 registros por dia
        num_registros = random.randint(4, 8)

        # Garante que todas as categorias apareçam ao longo do período
        # Alterna categorias para cobertura uniforme
        cats_dia = random.sample(todos_cat_ids, min(num_registros, len(todos_cat_ids)))
        if num_registros > len(todos_cat_ids):
            extras = random.choices(todos_cat_ids, k=num_registros - len(todos_cat_ids))
            cats_dia += extras

        for cat_id in cats_dia:
            fornecedores_cat = forn_por_cat[cat_id]
            forn_id = random.choice(fornecedores_cat)

            min_val, max_val = limites_categoria[cat_id]

            # Top 3 fornecedores recebem volume 2x maior
            if forn_id in top_3_forn:
                min_val = min_val * 1.5
                max_val = max_val * 2.0

            valor_total = round(random.uniform(min_val, max_val), 2)
            quantidade_itens = random.randint(20, 500)

            vendas.append((data_str, cat_id, forn_id, quantidade_itens, valor_total))

        data_atual += timedelta(days=1)

    cursor.executemany(
        'INSERT INTO vendas (data, categoria_id, fornecedor_id, quantidade_itens, valor_total) VALUES (?, ?, ?, ?, ?)',
        vendas
    )
    conn.commit()

    # Gera ticket_diario para cada dia dos últimos 12 meses
    # Ticket médio com tendência de crescimento leve ao longo dos meses
    ticket_diario = []
    data_atual = data_inicio
    total_dias = (hoje - data_inicio).days + 1
    dia_contador = 0

    while data_atual <= hoje:
        data_str = data_atual.strftime('%Y-%m-%d')

        # Tendência crescente: meses mais recentes têm ticket ligeiramente maior
        # Progresso de 0.0 (início) a 1.0 (hoje)
        progresso = dia_contador / total_dias if total_dias > 0 else 0

        # Ticket base entre 38 e 80, com acréscimo de até 15 conforme progresso
        ticket_base = random.uniform(38.0, 80.0)
        ticket_crescimento = progresso * 15.0
        ticket_medio = round(ticket_base + ticket_crescimento, 2)

        # Garante máximo de 95.00
        ticket_medio = min(ticket_medio, 95.0)

        num_transacoes = random.randint(180, 450)

        ticket_diario.append((data_str, num_transacoes, ticket_medio))

        data_atual += timedelta(days=1)
        dia_contador += 1

    cursor.executemany(
        'INSERT INTO ticket_diario (data, num_transacoes, ticket_medio) VALUES (?, ?, ?)',
        ticket_diario
    )

    conn.commit()
    conn.close()
