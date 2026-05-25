# Seed de dados para demonstração — Projeto 2 Gestão de Estoque
# Base Exata | Dados simulados de supermercado em Capivari, SP

import sqlite3
import random
from datetime import datetime, timedelta


def popular_banco(database_path):
    """Popula o banco com 30 produtos e 200 movimentações dos últimos 30 dias."""
    conn = sqlite3.connect(database_path)
    conn.execute('PRAGMA journal_mode=WAL;')
    cursor = conn.cursor()

    # 30 produtos de supermercado com dados realistas
    # (nome, categoria, qtd_atual, qtd_minima, preco_unitario, unidade)
    produtos = [
        ('Arroz Tipo 1 5kg',        'Mercearia',  42,  20, 28.90, 'pct'),
        ('Feijão Carioca 1kg',       'Mercearia',   8,  15,  9.50, 'pct'),
        ('Óleo de Soja 900ml',       'Mercearia',   0,  12,  7.80, 'un'),
        ('Macarrão Espaguete 500g',  'Mercearia',  55,  20,  4.20, 'pct'),
        ('Sal Refinado 1kg',         'Mercearia',  30,  10,  2.90, 'pct'),
        ('Açúcar Cristal 5kg',       'Mercearia',   5,  18, 24.50, 'pct'),
        ('Farinha de Trigo 1kg',     'Mercearia',  22,  15,  5.30, 'pct'),
        ('Molho de Tomate 340g',     'Mercearia',   3,  20,  3.40, 'un'),
        ('Coca-Cola 2L',             'Bebidas',    18,  24, 11.90, 'un'),
        ('Água Mineral 500ml',       'Bebidas',    60,  30,  1.80, 'un'),
        ('Suco de Laranja 1L',       'Bebidas',     7,  12,  8.50, 'cx'),
        ('Cerveja Lata 350ml',       'Bebidas',   120,  48,  3.90, 'un'),
        ('Refrigerante Guaraná 2L',  'Bebidas',     0,  12,  9.90, 'un'),
        ('Leite Integral 1L',        'Bebidas',    14,  30,  4.80, 'cx'),
        ('Banana Prata kg',          'Hortifrúti', 25,  10,  3.50, 'kg'),
        ('Maçã Fuji kg',             'Hortifrúti',  4,   8,  7.90, 'kg'),
        ('Tomate Salada kg',         'Hortifrúti', 12,  10,  5.60, 'kg'),
        ('Cebola kg',                'Hortifrúti',  2,   8,  4.20, 'kg'),
        ('Batata Inglesa kg',        'Hortifrúti', 18,  10,  3.80, 'kg'),
        ('Queijo Muçarela kg',       'Frios',       6,   5, 42.00, 'kg'),
        ('Presunto Fatiado 200g',    'Frios',       0,   8,  8.90, 'pct'),
        ('Margarina 500g',           'Frios',      15,  10,  6.40, 'pct'),
        ('Iogurte Natural 170g',     'Frios',       9,  12,  3.20, 'un'),
        ('Mortadela Fatiada 200g',   'Frios',       3,  10,  6.80, 'pct'),
        ('Detergente Líquido 500ml', 'Limpeza',    28,  15,  2.50, 'un'),
        ('Sabão em Pó 1kg',          'Limpeza',    11,  10, 12.90, 'cx'),
        ('Desinfetante 1L',          'Limpeza',     1,  10,  5.90, 'un'),
        ('Papel Higiênico 12un',     'Higiene',    22,  10, 18.90, 'pct'),
        ('Shampoo 400ml',            'Higiene',     8,   8, 13.50, 'un'),
        ('Sabonete 90g',             'Higiene',    35,  20,  2.20, 'un'),
    ]

    cursor.executemany('''
        INSERT INTO produtos (nome, categoria, quantidade_atual, quantidade_minima, preco_unitario, unidade)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', produtos)
    conn.commit()

    # Busca IDs dos produtos inseridos
    ids_produtos = [row[0] for row in cursor.execute('SELECT id FROM produtos').fetchall()]

    observacoes_entrada = [
        'Recebimento NF-e fornecedor',
        'Reposição de estoque',
        'Compra emergencial',
        'Entrega programada',
        'Devolução de cliente',
    ]
    observacoes_saida = [
        'Venda balcão',
        'Consumo interno',
        'Perda / vencimento',
        'Transferência filial',
        'Venda atacado',
    ]

    # 200 movimentações distribuídas nos últimos 30 dias
    movimentacoes = []
    agora = datetime.now()

    for _ in range(200):
        produto_id = random.choice(ids_produtos)
        tipo = 'entrada' if random.random() < 0.55 else 'saida'
        quantidade = random.randint(1, 50)
        dias_atras = random.randint(0, 29)
        horas_atras = random.randint(0, 23)
        data_hora = (agora - timedelta(days=dias_atras, hours=horas_atras)).strftime('%Y-%m-%d %H:%M:%S')
        observacao = random.choice(observacoes_entrada if tipo == 'entrada' else observacoes_saida)
        movimentacoes.append((produto_id, tipo, quantidade, data_hora, observacao))

    cursor.executemany('''
        INSERT INTO movimentacoes (produto_id, tipo, quantidade, data_hora, observacao)
        VALUES (?, ?, ?, ?, ?)
    ''', movimentacoes)

    conn.commit()
    conn.close()
