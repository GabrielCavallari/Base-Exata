# Seed de dados para demonstração — Projeto 6 Performance Comercial
# Base Exata | Dados simulados de performance comercial no interior de SP

import sqlite3
import random
from datetime import datetime, date, timedelta


def popular_banco(database_path):
    """Popula o banco com 6 vendedores e aproximadamente 1.000 registros de vendas nos últimos 6 meses."""
    conn = sqlite3.connect(database_path)
    conn.execute('PRAGMA journal_mode=WAL;')
    cursor = conn.cursor()

    # 1. Cadastrar os 6 vendedores representativos
    # (nome, regiao, meta_mensal)
    vendedores = [
        ('Carlos Silva',      'Capivari',      45000.00),
        ('Ana Souza',         'Rafard',        30000.00),
        ('Marcos Santos',     'Elias Fausto',  35000.00),
        ('Fernanda Costa',    'Piracicaba',    50000.00),
        ('Roberto Oliveira',  'Tietê',         40000.00),
        ('Juliana Lima',      'Saltinho',      32000.00)
    ]

    cursor.executemany('''
        INSERT INTO vendedores (nome, regiao, meta_mensal)
        VALUES (?, ?, ?)
    ''', vendedores)
    conn.commit()

    # Recupera os IDs gerados para associar às vendas
    cursor.execute('SELECT id, nome, meta_mensal FROM vendedores')
    rows_vendedores = cursor.fetchall()
    
    # Mapeamento do vendedor para seu ID e configurações de geração de vendas
    # Para garantir faturamentos realistas que correspondam aos requisitos:
    # - Fernanda Costa (Piracicaba): bate a meta (~108%)
    # - Carlos Silva (Capivari): bate a meta (~107%)
    # - Juliana Lima (Saltinho): bate a meta de raspão ou fica em 100% (~101%)
    # - Roberto Oliveira (Tietê): fica bem próximo (~96%)
    # - Ana Souza (Rafard): fica próxima (~93%)
    # - Marcos Santos (Elias Fausto): fica próximo ou abaixo (~88%)
    
    config_vendedores = {
        'Fernanda Costa':   {'id': None, 'peso': 0.21, 'min_val': 800.0, 'max_val': 3100.0},
        'Carlos Silva':     {'id': None, 'peso': 0.19, 'min_val': 800.0, 'max_val': 2900.0},
        'Roberto Oliveira': {'id': None, 'peso': 0.16, 'min_val': 700.0, 'max_val': 2600.0},
        'Marcos Santos':    {'id': None, 'peso': 0.15, 'min_val': 600.0, 'max_val': 2300.0},
        'Juliana Lima':     {'id': None, 'peso': 0.14, 'min_val': 700.0, 'max_val': 2700.0},
        'Ana Souza':        {'id': None, 'peso': 0.15, 'min_val': 600.0, 'max_val': 2200.0}
    }

    vendedores_id_pool = []
    pesos = []
    
    for row in rows_vendedores:
        vid, nome, meta = row
        vendedor_config = config_vendedores[nome]
        vendedor_config['id'] = vid
        vendedores_id_pool.append(vendedor_config)
        pesos.append(vendedor_config['peso'])

    # 2. Gerar registros de vendas nos últimos 6 meses (180 dias)
    hoje = date.today()
    data_inicio = hoje - timedelta(days=179)
    
    vendas = []
    data_atual = data_inicio

    while data_atual <= hoje:
        data_str = data_atual.strftime('%Y-%m-%d')
        
        # Gerar entre 5 e 6 vendas por dia (média de ~5.5 vendas/dia, total de ~990 vendas em 180 dias)
        num_vendas_dia = random.randint(5, 6)
        
        for _ in range(num_vendas_dia):
            # Escolher vendedor proporcionalmente ao seu peso comercial
            vendedor_config = random.choices(vendedores_id_pool, weights=pesos)[0]
            vendedor_id = vendedor_config['id']
            
            # Definir status (Conversão de ~85% concluídas)
            status = 'Concluída' if random.random() < 0.85 else 'Cancelada'
            
            # Valor da venda baseado na faixa configurada para o vendedor
            valor = round(random.uniform(vendedor_config['min_val'], vendedor_config['max_val']), 2)
            
            vendas.append((vendedor_id, data_str, valor, status))
            
        data_atual += timedelta(days=1)

    # Inserir vendas em lote no banco
    cursor.executemany('''
        INSERT INTO vendas (vendedor_id, data, valor, status)
        VALUES (?, ?, ?, ?)
    ''', vendas)
    
    conn.commit()
    conn.close()
    
    print(f"Seed realizado com sucesso! {len(vendedores)} vendedores e {len(vendas)} vendas inseridas no banco.")


if __name__ == '__main__':
    # Se rodar este script diretamente, popula localmente em database.db
    popular_banco('database.db')
