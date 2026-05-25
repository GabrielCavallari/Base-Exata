"""
Seed de dados fictícios para demonstração.
30 produtos reais de comércio/varejo + 200 movimentações.
"""

import sqlite3
import random
from datetime import datetime, timedelta


def seed_demo_data(db_path):
    # Seed fixo para gerar dados sempre idênticos (disco efêmero do Render)
    random.seed(42)
    db = sqlite3.connect(db_path)
    cur = db.cursor()

    # ── Categorias ──
    categorias = [
        "Bebidas", "Limpeza", "Higiene", "Mercearia",
        "Hortifrúti", "Padaria", "Carnes e Frios",
        "Materiais de Escritório"
    ]
    for cat in categorias:
        cur.execute("INSERT OR IGNORE INTO categorias (nome) VALUES (?)", (cat,))
    db.commit()

    cat_map = {}
    for row in cur.execute("SELECT id, nome FROM categorias"):
        cat_map[row[1]] = row[0]

    # ── Produtos (30) ──
    produtos = [
        # Bebidas
        ("Água Mineral 500ml", "BEB-001", "Bebidas", 0.80, 2.50, 150, 30, "Distribuidora São Jorge"),
        ("Refrigerante Cola 2L", "BEB-002", "Bebidas", 3.50, 7.99, 80, 20, "Distribuidora São Jorge"),
        ("Suco de Laranja 1L", "BEB-003", "Bebidas", 4.20, 8.90, 45, 15, "Polpa Frutas Ltda"),
        ("Cerveja Lata 350ml", "BEB-004", "Bebidas", 2.10, 4.99, 200, 50, "Distribuidora São Jorge"),
        # Limpeza
        ("Detergente 500ml", "LIM-001", "Limpeza", 1.20, 3.49, 60, 15, "Química Limpa"),
        ("Água Sanitária 1L", "LIM-002", "Limpeza", 2.00, 4.99, 40, 10, "Química Limpa"),
        ("Sabão em Pó 1kg", "LIM-003", "Limpeza", 5.50, 12.90, 35, 10, "Química Limpa"),
        ("Esponja Multiuso (pac 3un)", "LIM-004", "Limpeza", 1.50, 3.99, 8, 20, "Casa & Cia"),
        # Higiene
        ("Papel Higiênico 12 rolos", "HIG-001", "Higiene", 8.00, 18.90, 25, 10, "Papéis Brasil"),
        ("Sabonete 90g", "HIG-002", "Higiene", 1.00, 2.99, 70, 20, "Higiene Total"),
        ("Creme Dental 90g", "HIG-003", "Higiene", 2.50, 5.99, 40, 15, "Higiene Total"),
        ("Shampoo 350ml", "HIG-004", "Higiene", 6.00, 14.90, 30, 10, "Higiene Total"),
        # Mercearia
        ("Arroz 5kg", "MER-001", "Mercearia", 14.00, 27.90, 60, 15, "Cereais do Interior"),
        ("Feijão Carioca 1kg", "MER-002", "Mercearia", 5.00, 9.90, 50, 15, "Cereais do Interior"),
        ("Macarrão Espaguete 500g", "MER-003", "Mercearia", 2.20, 4.99, 80, 20, "Massas Bella"),
        ("Óleo de Soja 900ml", "MER-004", "Mercearia", 4.50, 8.99, 45, 15, "Óleos Puros"),
        ("Açúcar 1kg", "MER-005", "Mercearia", 3.00, 5.99, 55, 15, "Cereais do Interior"),
        ("Café 500g", "MER-006", "Mercearia", 8.00, 16.90, 6, 15, "Torrefação Capivari"),
        # Hortifrúti
        ("Banana Prata (kg)", "HOR-001", "Hortifrúti", 2.50, 5.99, 30, 10, "Sítio Boa Vista"),
        ("Tomate (kg)", "HOR-002", "Hortifrúti", 3.00, 7.99, 20, 10, "Sítio Boa Vista"),
        ("Batata (kg)", "HOR-003", "Hortifrúti", 2.00, 4.99, 40, 10, "Sítio Boa Vista"),
        ("Cebola (kg)", "HOR-004", "Hortifrúti", 2.50, 5.49, 25, 10, "Sítio Boa Vista"),
        # Padaria
        ("Pão Francês (kg)", "PAD-001", "Padaria", 6.00, 14.90, 15, 5, "Produção Própria"),
        ("Bolo de Chocolate fatia", "PAD-002", "Padaria", 2.00, 6.90, 3, 5, "Produção Própria"),
        ("Biscoito Amanteigado 200g", "PAD-003", "Padaria", 3.50, 7.99, 25, 10, "Massas Bella"),
        # Carnes e Frios
        ("Peito de Frango (kg)", "CAR-001", "Carnes e Frios", 12.00, 22.90, 2, 10, "Frigorífico Regional"),
        ("Presunto Fatiado (kg)", "CAR-002", "Carnes e Frios", 18.00, 34.90, 8, 5, "Frigorífico Regional"),
        ("Linguiça Toscana (kg)", "CAR-003", "Carnes e Frios", 14.00, 26.90, 12, 5, "Frigorífico Regional"),
        # Materiais de Escritório
        ("Resma Papel A4", "ESC-001", "Materiais de Escritório", 18.00, 32.90, 20, 5, "Papéis Brasil"),
        ("Caneta Esferográfica Azul", "ESC-002", "Materiais de Escritório", 0.80, 2.50, 100, 20, "Papelaria Express"),
    ]

    for p in produtos:
        cur.execute("""
            INSERT INTO produtos (nome, sku, categoria_id, preco_custo, preco_venda,
                                  estoque_atual, estoque_minimo, fornecedor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (p[0], p[1], cat_map[p[2]], p[3], p[4], p[5], p[6], p[7]))
    db.commit()

    # Obter IDs dos produtos
    prod_ids = [row[0] for row in cur.execute("SELECT id FROM produtos")]

    # ── Movimentações (200+) ──
    observacoes_entrada = [
        "Reposição semanal",
        "Pedido fornecedor",
        "Transferência entre lojas",
        "Compra direta",
        "Reposição de emergência",
        "Novo fornecedor",
        "Promoção — compra extra",
        "Estoque de segurança",
    ]
    observacoes_saida = [
        "Venda balcão",
        "Venda atacado",
        "Perda por validade",
        "Avaria",
        "Consumo interno",
        "Venda delivery",
        "Promoção especial",
        "Devolução ao fornecedor",
    ]

    movimentacoes = []
    # Data base fixa para que os dados sejam idênticos em cada restart
    data_base = datetime(2026, 5, 20, 12, 0, 0)
    for _ in range(220):
        prod_id = random.choice(prod_ids)
        tipo = random.choices(["entrada", "saida"], weights=[40, 60])[0]
        quantidade = random.randint(1, 30) if tipo == "entrada" else random.randint(1, 15)
        dias_atras = random.randint(0, 45)
        hora = random.randint(7, 20)
        minuto = random.randint(0, 59)
        data = (data_base - timedelta(days=dias_atras)).replace(
            hour=hora, minute=minuto, second=0
        ).strftime("%Y-%m-%d %H:%M:%S")
        obs = random.choice(
            observacoes_entrada if tipo == "entrada" else observacoes_saida
        )
        movimentacoes.append((prod_id, tipo, quantidade, data, obs))

    # Sort by date for consistency
    movimentacoes.sort(key=lambda x: x[3])

    for m in movimentacoes:
        cur.execute("""
            INSERT INTO movimentacoes (produto_id, tipo, quantidade, data, observacao)
            VALUES (?, ?, ?, ?, ?)
        """, m)

    db.commit()

    # Recalculate actual stock based on movements
    for pid in prod_ids:
        base = cur.execute(
            "SELECT estoque_atual FROM produtos WHERE id=?", (pid,)
        ).fetchone()[0]
        entradas = cur.execute(
            "SELECT COALESCE(SUM(quantidade),0) FROM movimentacoes WHERE produto_id=? AND tipo='entrada'",
            (pid,)
        ).fetchone()[0]
        saidas = cur.execute(
            "SELECT COALESCE(SUM(quantidade),0) FROM movimentacoes WHERE produto_id=? AND tipo='saida'",
            (pid,)
        ).fetchone()[0]
        novo_estoque = max(base + entradas - saidas, 0)
        cur.execute(
            "UPDATE produtos SET estoque_atual=? WHERE id=?", (novo_estoque, pid)
        )

    db.commit()
    db.close()
    print(f"✅ Seed: {len(produtos)} produtos + {len(movimentacoes)} movimentações")


if __name__ == "__main__":
    import os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "estoque.db")
    from app import init_db
    init_db()
    seed_demo_data(db_path)
