# Seed de dados para demonstração — Projeto 1 Dashboard de Vendas
# Base Exata | 6 meses de vendas fictícias de supermercado em Capivari, SP

import sqlite3
import random
from datetime import datetime, timedelta


# 50 SKUs em 6 categorias com custo e preço de venda realistas
PRODUTOS = [
    # (nome, categoria, custo, preco_venda)
    # Mercearia
    ('Arroz Tipo 1 5kg',        'Mercearia',  22.00, 28.90),
    ('Feijão Carioca 1kg',      'Mercearia',   7.20,  9.50),
    ('Óleo de Soja 900ml',      'Mercearia',   6.10,  7.80),
    ('Macarrão Espaguete 500g', 'Mercearia',   2.90,  4.20),
    ('Sal Refinado 1kg',        'Mercearia',   1.80,  2.90),
    ('Açúcar Cristal 5kg',      'Mercearia',  19.00, 24.50),
    ('Farinha de Trigo 1kg',    'Mercearia',   3.80,  5.30),
    ('Molho de Tomate 340g',    'Mercearia',   2.20,  3.40),
    ('Azeite Extravirgem 500ml','Mercearia',  18.50, 28.90),
    # Produtos com margem negativa (custo > preço — para o case narrativo)
    ('Café Torrado 500g',       'Mercearia',  16.00, 14.90),
    ('Achocolatado 400g',       'Mercearia',  12.50, 11.80),

    # Bebidas
    ('Coca-Cola 2L',            'Bebidas',     8.50, 11.90),
    ('Água Mineral 500ml',      'Bebidas',     0.90,  1.80),
    ('Suco de Laranja 1L',      'Bebidas',     5.80,  8.50),
    ('Cerveja Lata 350ml',      'Bebidas',     2.50,  3.90),
    ('Refrigerante Guaraná 2L', 'Bebidas',     6.80,  9.90),
    ('Leite Integral 1L',       'Bebidas',     3.50,  4.80),
    ('Energético 250ml',        'Bebidas',     4.20,  6.90),
    ('Vinho Tinto 750ml',       'Bebidas',    22.00, 38.90),
    # Margem negativa intencional
    ('Isotônico 500ml',         'Bebidas',     5.50,  4.90),

    # Hortifrúti
    ('Banana Prata kg',         'Hortifrúti',  2.00,  3.50),
    ('Maçã Fuji kg',            'Hortifrúti',  5.00,  7.90),
    ('Tomate Salada kg',        'Hortifrúti',  3.80,  5.60),
    ('Cebola kg',               'Hortifrúti',  2.80,  4.20),
    ('Batata Inglesa kg',       'Hortifrúti',  2.50,  3.80),
    ('Alface Crespa un',        'Hortifrúti',  1.80,  2.90),
    ('Laranja Pera kg',         'Hortifrúti',  2.20,  3.60),
    ('Cenoura kg',              'Hortifrúti',  3.00,  4.50),

    # Frios
    ('Queijo Muçarela kg',      'Frios',      30.00, 42.00),
    ('Presunto Cozido kg',      'Frios',      18.00, 28.90),
    ('Margarina 500g',          'Frios',       4.50,  6.40),
    ('Iogurte Natural 170g',    'Frios',       2.10,  3.20),
    ('Mortadela Fatiada 200g',  'Frios',       4.50,  6.80),
    ('Requeijão 200g',          'Frios',       5.80,  8.90),
    # Margem negativa intencional
    ('Manteiga com Sal 200g',   'Frios',      10.00,  8.50),

    # Limpeza
    ('Detergente Líquido 500ml','Limpeza',     1.60,  2.50),
    ('Sabão em Pó 1kg',         'Limpeza',     9.00, 12.90),
    ('Desinfetante 1L',         'Limpeza',     3.80,  5.90),
    ('Amaciante 2L',            'Limpeza',     8.00, 12.50),
    ('Esponja de Cozinha 3un',  'Limpeza',     2.00,  3.50),
    ('Água Sanitária 1L',       'Limpeza',     2.80,  4.20),
    ('Rodo c/ Cabo un',         'Limpeza',     9.00, 14.90),

    # Higiene
    ('Papel Higiênico 12un',    'Higiene',    13.00, 18.90),
    ('Shampoo 400ml',           'Higiene',     8.50, 13.50),
    ('Sabonete 90g',            'Higiene',     1.40,  2.20),
    ('Creme Dental 90g',        'Higiene',     3.20,  5.50),
    ('Desodorante Roll-on 50ml','Higiene',     6.00,  9.90),
    ('Absorvente c/abas 8un',   'Higiene',     4.50,  7.90),
    ('Fio Dental 50m',          'Higiene',     2.50,  4.20),
    ('Escova de Dentes un',     'Higiene',     3.00,  5.50),
]

# Sazonalidade por mês (fator multiplicador de volume de vendas)
SAZONALIDADE = {
    1: 0.95,  # Janeiro
    2: 0.90,  # Fevereiro
    3: 0.85,  # Março
    4: 0.88,  # Abril
    5: 0.92,  # Maio
    6: 1.05,  # Junho (festa junina)
    7: 1.10,  # Julho (férias)
    8: 0.95,  # Agosto
    9: 0.90,  # Setembro
    10: 0.95, # Outubro
    11: 1.10, # Novembro (black friday)
    12: 1.30, # Dezembro (natal)
}

STATUS_OPCOES = ['Concluída', 'Concluída', 'Concluída', 'Concluída', 'Cancelada', 'Em processamento']


def popular_banco(database_path):
    """Popula o banco com 50 produtos e 6 meses de vendas."""
    conn = sqlite3.connect(database_path)
    conn.execute('PRAGMA journal_mode=WAL;')
    cursor = conn.cursor()

    # Insere produtos
    cursor.executemany(
        'INSERT INTO produtos (nome, categoria, custo) VALUES (?, ?, ?)',
        [(nome, cat, custo) for nome, cat, custo, _ in PRODUTOS]
    )
    conn.commit()

    ids_produtos = [r[0] for r in cursor.execute('SELECT id FROM produtos').fetchall()]
    preco_por_id = {
        ids_produtos[i]: PRODUTOS[i][3] for i in range(len(PRODUTOS))
    }

    # Gera 6 meses de vendas a partir do mês atual retroativo
    hoje = datetime.now()
    inicio = hoje - timedelta(days=180)

    vendas = []
    data_atual = inicio

    while data_atual <= hoje:
        mes = data_atual.month
        fator = SAZONALIDADE.get(mes, 1.0)

        # Entre 8 e 25 vendas por dia, ajustadas pela sazonalidade
        num_vendas_dia = int(random.randint(8, 25) * fator)

        for _ in range(num_vendas_dia):
            produto_id = random.choice(ids_produtos)
            preco = preco_por_id[produto_id]
            # Variação de preço de ±5% para simular promoções
            preco_final = round(preco * random.uniform(0.95, 1.05), 2)
            quantidade = random.randint(1, 8)
            status = random.choice(STATUS_OPCOES)
            vendas.append((produto_id, quantidade, preco_final,
                           data_atual.strftime('%Y-%m-%d'), status))

        data_atual += timedelta(days=1)

    cursor.executemany(
        'INSERT INTO vendas (produto_id, quantidade, preco_unitario, data_venda, status) VALUES (?, ?, ?, ?, ?)',
        vendas
    )
    conn.commit()
    conn.close()
