# Seed de dados para demonstração — Projeto 5 Análise de Sazonalidade e Demanda
# Base Exata | Dados simulados de supermercado em Capivari, SP

import sqlite3
import random
from datetime import date, timedelta

# Configurações dos produtos, bases diárias, preços e fatores sazonais
PRODUTOS_CONFIG = {
    1: {
        "nome": "Arroz Tipo 1 5kg",
        "categoria": "Mercearia",
        "unidade": "pc",
        "base": 45,
        "preco": 24.90,
        "sazonalidade": {1: 1.30, 2: 1.30, 6: 0.85, 7: 0.85}
    },
    2: {
        "nome": "Feijão Carioca 1kg",
        "categoria": "Mercearia",
        "unidade": "pc",
        "base": 38,
        "preco": 7.49,
        "sazonalidade": {1: 1.25, 2: 1.25, 3: 1.25}
    },
    3: {
        "nome": "Óleo de Soja 900ml",
        "categoria": "Mercearia",
        "unidade": "pc",
        "base": 30,
        "preco": 5.99,
        "sazonalidade": {6: 1.20, 7: 1.20, 8: 1.20, 12: 0.90}
    },
    4: {
        "nome": "Açúcar Cristal 5kg",
        "categoria": "Mercearia",
        "unidade": "pc",
        "base": 28,
        "preco": 18.90,
        "sazonalidade": {6: 1.40, 7: 1.40, 8: 1.40, 1: 0.90, 2: 0.90}
    },
    5: {
        "nome": "Cerveja Pilsen Lata 350ml",
        "categoria": "Bebidas",
        "unidade": "un",
        "base": 80,
        "preco": 3.49,
        "sazonalidade": {11: 1.70, 12: 1.70, 1: 1.70, 2: 1.70, 3: 1.70, 6: 0.60, 7: 0.60, 8: 0.60}
    },
    6: {
        "nome": "Refrigerante Cola 2L",
        "categoria": "Bebidas",
        "unidade": "un",
        "base": 60,
        "preco": 8.99,
        "sazonalidade": {11: 1.50, 12: 1.50, 1: 1.50, 2: 1.50, 3: 1.50, 6: 0.75, 7: 0.75, 8: 0.75}
    },
    7: {
        "nome": "Água Mineral 500ml",
        "categoria": "Bebidas",
        "unidade": "un",
        "base": 120,
        "preco": 1.49,
        "sazonalidade": {12: 1.60, 1: 1.60, 2: 1.60, 3: 1.60, 6: 0.70, 7: 0.70, 8: 0.70}
    },
    8: {
        "nome": "Frango Inteiro Kg",
        "categoria": "Açougue",
        "unidade": "kg",
        "base": 55,
        "preco": 14.90,
        "sazonalidade": {6: 1.25, 7: 1.25}
    },
    9: {
        "nome": "Sabão em Pó 1kg",
        "categoria": "Limpeza",
        "unidade": "pc",
        "base": 22,
        "preco": 9.99,
        "sazonalidade": {1: 1.20, 2: 1.20}
    },
    10: {
        "nome": "Papel Higiênico 12 rolos",
        "categoria": "Higiene",
        "unidade": "pc",
        "base": 18,
        "preco": 18.90,
        "sazonalidade": {1: 1.10}
    }
}


def seed_database(database_path):
    """Popula o banco de dados com produtos, vendas diárias e previsões sazonais."""
    conn = sqlite3.connect(database_path)
    conn.execute('PRAGMA journal_mode=WAL;')
    cursor = conn.cursor()

    # 1. Inserir produtos
    print("Semeando produtos...")
    produtos_data = []
    for pid, config in PRODUTOS_CONFIG.items():
        produtos_data.append((pid, config["nome"], config["categoria"], config["unidade"]))

    cursor.executemany('''
        INSERT INTO produtos (id, nome, categoria, unidade)
        VALUES (?, ?, ?, ?)
    ''', produtos_data)
    conn.commit()

    # 2. Inserir vendas diárias
    # 730 dias encerrando hoje para manter a demo sempre recente em bancos novos.
    print("Semeando vendas diárias (7.300 registros)...")
    vendas_data = []
    data_inicio = date.today() - timedelta(days=729)

    for i in range(730):
        data_atual = data_inicio + timedelta(days=i)
        data_str = data_atual.strftime('%Y-%m-%d')
        mes_atual = data_atual.month

        for pid, config in PRODUTOS_CONFIG.items():
            base = config["base"]
            preco = config["preco"]
            fator_sazonal = config["sazonalidade"].get(mes_atual, 1.0)
            
            # Cálculo da quantidade com variação sazonal
            qtd_esperada = base * fator_sazonal
            
            # Adiciona variação aleatória de ±10%
            variacao = random.uniform(0.90, 1.10)
            quantidade = int(qtd_esperada * variacao)
            
            # Garante que a quantidade seja sempre pelo menos 1
            if quantidade < 1:
                quantidade = 1

            vendas_data.append((pid, data_str, quantidade, preco))

    cursor.executemany('''
        INSERT INTO vendas_diarias (produto_id, data, quantidade, valor_unitario)
        VALUES (?, ?, ?, ?)
    ''', vendas_data)
    conn.commit()

    # 3. Inserir previsões mensais
    # 1 linha por produto por mês (12 meses × 10 produtos = 120 linhas)
    print("Semeando previsões de demanda (120 registros)...")
    previsoes_data = []
    for mes in range(1, 13):
        for pid, config in PRODUTOS_CONFIG.items():
            base = config["base"]
            fator_sazonal = config["sazonalidade"].get(mes, 1.0)
            
            # Fórmula: base_diaria * fator_sazonal * 30 (arredondado para inteiro)
            quantidade_prevista = int(round(base * fator_sazonal * 30))
            if quantidade_prevista < 1:
                quantidade_prevista = 1

            previsoes_data.append((pid, mes, quantidade_prevista))

    cursor.executemany('''
        INSERT INTO previsoes (produto_id, mes, quantidade_prevista)
        VALUES (?, ?, ?)
    ''', previsoes_data)
    
    conn.commit()
    conn.close()
    print("Seed concluído com sucesso!")


if __name__ == '__main__':
    # Para testes individuais
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'database.db')
    
    # Criar tabelas se rodando diretamente
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.execute('DROP TABLE IF EXISTS produtos')
    conn.execute('DROP TABLE IF EXISTS vendas_diarias')
    conn.execute('DROP TABLE IF EXISTS previsoes')
    conn.execute('''
        CREATE TABLE produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            unidade TEXT NOT NULL DEFAULT 'un'
        )
    ''')
    conn.execute('''
        CREATE TABLE vendas_diarias (
            id INTEGER PRIMARY KEY,
            produto_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            valor_unitario REAL NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    ''')
    conn.execute('''
        CREATE TABLE previsoes (
            id INTEGER PRIMARY KEY,
            produto_id INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            quantidade_prevista INTEGER NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    ''')
    conn.commit()
    conn.close()
    
    seed_database(DB_PATH)
