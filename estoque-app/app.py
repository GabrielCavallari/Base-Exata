"""
Base Exata — Sistema de Gestão de Estoque
Projeto-demo para consultoria em dados e automação.
Flask + SQLite + Bootstrap 5 + Chart.js
"""

import os
import sqlite3
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, g
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "base-exata-demo-2026")
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "estoque.db")


# ──────────────────────────────────────────────
#  DATABASE HELPERS
# ──────────────────────────────────────────────

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    );

    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        sku TEXT NOT NULL UNIQUE,
        categoria_id INTEGER NOT NULL,
        preco_custo REAL NOT NULL DEFAULT 0,
        preco_venda REAL NOT NULL DEFAULT 0,
        estoque_atual INTEGER NOT NULL DEFAULT 0,
        estoque_minimo INTEGER NOT NULL DEFAULT 5,
        fornecedor TEXT DEFAULT '',
        ativo INTEGER NOT NULL DEFAULT 1,
        criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    );

    CREATE TABLE IF NOT EXISTS movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER NOT NULL,
        tipo TEXT NOT NULL CHECK(tipo IN ('entrada','saida')),
        quantidade INTEGER NOT NULL,
        data TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        observacao TEXT DEFAULT '',
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
    );

    CREATE INDEX IF NOT EXISTS idx_mov_data ON movimentacoes(data);
    CREATE INDEX IF NOT EXISTS idx_mov_produto ON movimentacoes(produto_id);
    CREATE INDEX IF NOT EXISTS idx_prod_categoria ON produtos(categoria_id);

    CREATE TABLE IF NOT EXISTS demo_meta (
        chave TEXT PRIMARY KEY,
        valor TEXT NOT NULL
    );
    """)
    db.commit()
    db.close()


def atualizar_datas_demo():
    """Mantem as datas demonstrativas alinhadas ao dia atual."""
    db = sqlite3.connect(DATABASE)
    try:
        cur = db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS demo_meta (
                chave TEXT PRIMARY KEY,
                valor TEXT NOT NULL
            )
        """)
        row = cur.execute("SELECT MAX(date(data)) FROM movimentacoes").fetchone()
        max_data = row[0] if row else None

        if not max_data:
            db.commit()
            return

        hoje = datetime.now().date()
        maior_data = datetime.strptime(max_data, "%Y-%m-%d").date()
        dias = (hoje - maior_data).days

        if dias > 0:
            modificador = f"+{dias} days"
            cur.execute("UPDATE movimentacoes SET data = datetime(data, ?)", (modificador,))
            cur.execute("UPDATE produtos SET criado_em = datetime(criado_em, ?)", (modificador,))

        cur.execute(
            "INSERT OR REPLACE INTO demo_meta (chave, valor) VALUES (?, ?)",
            ("last_demo_refresh_date", hoje.isoformat()),
        )
        cur.execute(
            "INSERT OR REPLACE INTO demo_meta (chave, valor) VALUES (?, ?)",
            ("last_max_data_detected", max_data),
        )
        db.commit()
    finally:
        db.close()


@app.before_request
def refresh_demo_dates_once_per_day():
    hoje = datetime.now().strftime("%Y-%m-%d")
    if app.config.get("_demo_dates_checked_on") != hoje:
        atualizar_datas_demo()
        app.config["_demo_dates_checked_on"] = hoje


# ──────────────────────────────────────────────
#  TEMPLATE FILTERS
# ──────────────────────────────────────────────

@app.template_filter("brl")
def format_brl(value):
    try:
        return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"


@app.template_filter("data_br")
def format_data_br(value):
    try:
        dt = datetime.strptime(value[:19], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        try:
            dt = datetime.strptime(value[:10], "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
        except Exception:
            return value


# ──────────────────────────────────────────────
#  CONTEXT PROCESSOR (globals for all templates)
# ──────────────────────────────────────────────

@app.context_processor
def inject_globals():
    try:
        db = get_db()
        alerta_count = db.execute(
            "SELECT COUNT(*) FROM produtos WHERE ativo=1 AND estoque_atual < estoque_minimo"
        ).fetchone()[0]
    except Exception:
        alerta_count = 0
    return {"alerta_count": alerta_count, "now": datetime.now()}


# ──────────────────────────────────────────────
#  DASHBOARD
# ──────────────────────────────────────────────

@app.route("/")
def dashboard():
    db = get_db()

    total_produtos = db.execute(
        "SELECT COUNT(*) FROM produtos WHERE ativo=1"
    ).fetchone()[0]

    valor_estoque = db.execute(
        "SELECT COALESCE(SUM(estoque_atual * preco_custo), 0) FROM produtos WHERE ativo=1"
    ).fetchone()[0]

    valor_venda = db.execute(
        "SELECT COALESCE(SUM(estoque_atual * preco_venda), 0) FROM produtos WHERE ativo=1"
    ).fetchone()[0]

    abaixo_minimo = db.execute(
        "SELECT COUNT(*) FROM produtos WHERE ativo=1 AND estoque_atual < estoque_minimo"
    ).fetchone()[0]

    hoje = datetime.now().strftime("%Y-%m-%d")
    mov_hoje = db.execute(
        "SELECT COUNT(*) FROM movimentacoes WHERE date(data)=?", (hoje,)
    ).fetchone()[0]

    # Últimos 7 dias para gráfico
    dados_7d = []
    for i in range(6, -1, -1):
        dia = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        label = (datetime.now() - timedelta(days=i)).strftime("%d/%m")
        row = db.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN tipo='entrada' THEN quantidade ELSE 0 END), 0) as entradas,
                COALESCE(SUM(CASE WHEN tipo='saida' THEN quantidade ELSE 0 END), 0) as saidas
            FROM movimentacoes WHERE date(data)=?
        """, (dia,)).fetchone()
        dados_7d.append({
            "label": label,
            "entradas": row["entradas"],
            "saidas": row["saidas"]
        })

    # Top 5 produtos com menor estoque relativo
    alertas_top = db.execute("""
        SELECT p.nome, p.estoque_atual, p.estoque_minimo, c.nome as categoria
        FROM produtos p JOIN categorias c ON p.categoria_id = c.id
        WHERE p.ativo=1 AND p.estoque_atual < p.estoque_minimo
        ORDER BY (p.estoque_atual * 1.0 / MAX(p.estoque_minimo, 1)) ASC
        LIMIT 5
    """).fetchall()

    # Últimas 10 movimentações
    ultimas_mov = db.execute("""
        SELECT m.*, p.nome as produto_nome, p.sku
        FROM movimentacoes m JOIN produtos p ON m.produto_id = p.id
        ORDER BY m.data DESC LIMIT 10
    """).fetchall()

    # Valor por categoria (para gráfico donut)
    valor_categoria = [
        dict(row) for row in db.execute("""
        SELECT c.nome, COALESCE(SUM(p.estoque_atual * p.preco_custo), 0) as valor
        FROM produtos p JOIN categorias c ON p.categoria_id = c.id
        WHERE p.ativo=1
        GROUP BY c.id ORDER BY valor DESC
    """).fetchall()
    ]

    return render_template("dashboard.html",
        total_produtos=total_produtos,
        valor_estoque=valor_estoque,
        valor_venda=valor_venda,
        abaixo_minimo=abaixo_minimo,
        mov_hoje=mov_hoje,
        dados_7d=dados_7d,
        alertas_top=alertas_top,
        ultimas_mov=ultimas_mov,
        valor_categoria=valor_categoria,
    )


# ──────────────────────────────────────────────
#  PRODUTOS — CRUD
# ──────────────────────────────────────────────

@app.route("/produtos")
def produtos_lista():
    db = get_db()
    busca = request.args.get("busca", "").strip()
    cat_id = request.args.get("categoria", "")
    ordem = request.args.get("ordem", "nome")

    query = """
        SELECT p.*, c.nome as categoria_nome
        FROM produtos p JOIN categorias c ON p.categoria_id = c.id
        WHERE p.ativo=1
    """
    params = []

    if busca:
        query += " AND (p.nome LIKE ? OR p.sku LIKE ? OR p.fornecedor LIKE ?)"
        like = f"%{busca}%"
        params.extend([like, like, like])

    if cat_id:
        query += " AND p.categoria_id=?"
        params.append(int(cat_id))

    order_map = {
        "nome": "p.nome ASC",
        "estoque": "p.estoque_atual ASC",
        "valor": "(p.estoque_atual * p.preco_custo) DESC",
        "sku": "p.sku ASC",
    }
    query += f" ORDER BY {order_map.get(ordem, 'p.nome ASC')}"

    produtos = db.execute(query, params).fetchall()
    categorias = db.execute("SELECT * FROM categorias ORDER BY nome").fetchall()

    return render_template("produtos.html",
        produtos=produtos,
        categorias=categorias,
        busca=busca,
        cat_id=cat_id,
        ordem=ordem,
    )


@app.route("/produtos/novo", methods=["GET", "POST"])
def produto_novo():
    db = get_db()
    if request.method == "POST":
        try:
            db.execute("""
                INSERT INTO produtos (nome, sku, categoria_id, preco_custo, preco_venda,
                                      estoque_atual, estoque_minimo, fornecedor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.form["nome"],
                request.form["sku"].upper(),
                int(request.form["categoria_id"]),
                float(request.form["preco_custo"]),
                float(request.form["preco_venda"]),
                int(request.form["estoque_atual"]),
                int(request.form["estoque_minimo"]),
                request.form.get("fornecedor", ""),
            ))
            db.commit()
            flash("Produto cadastrado com sucesso!", "success")
            return redirect(url_for("produtos_lista"))
        except sqlite3.IntegrityError:
            flash("SKU já existe. Use um código diferente.", "danger")
        except Exception as e:
            flash(f"Erro ao cadastrar: {e}", "danger")

    categorias = db.execute("SELECT * FROM categorias ORDER BY nome").fetchall()
    return render_template("produto_form.html", produto=None, categorias=categorias)


@app.route("/produtos/<int:id>/editar", methods=["GET", "POST"])
def produto_editar(id):
    db = get_db()
    produto = db.execute("SELECT * FROM produtos WHERE id=?", (id,)).fetchone()
    if not produto:
        flash("Produto não encontrado.", "warning")
        return redirect(url_for("produtos_lista"))

    if request.method == "POST":
        try:
            db.execute("""
                UPDATE produtos SET nome=?, sku=?, categoria_id=?, preco_custo=?,
                    preco_venda=?, estoque_minimo=?, fornecedor=?
                WHERE id=?
            """, (
                request.form["nome"],
                request.form["sku"].upper(),
                int(request.form["categoria_id"]),
                float(request.form["preco_custo"]),
                float(request.form["preco_venda"]),
                int(request.form["estoque_minimo"]),
                request.form.get("fornecedor", ""),
                id,
            ))
            db.commit()
            flash("Produto atualizado!", "success")
            return redirect(url_for("produtos_lista"))
        except Exception as e:
            flash(f"Erro ao atualizar: {e}", "danger")

    categorias = db.execute("SELECT * FROM categorias ORDER BY nome").fetchall()
    return render_template("produto_form.html", produto=produto, categorias=categorias)


@app.route("/produtos/<int:id>/excluir", methods=["POST"])
def produto_excluir(id):
    db = get_db()
    db.execute("UPDATE produtos SET ativo=0 WHERE id=?", (id,))
    db.commit()
    flash("Produto removido.", "info")
    return redirect(url_for("produtos_lista"))


# ──────────────────────────────────────────────
#  MOVIMENTAÇÕES
# ──────────────────────────────────────────────

@app.route("/movimentacoes")
def movimentacoes_lista():
    db = get_db()
    tipo = request.args.get("tipo", "")
    data_de = request.args.get("data_de", "")
    data_ate = request.args.get("data_ate", "")
    produto_id = request.args.get("produto_id", "")

    query = """
        SELECT m.*, p.nome as produto_nome, p.sku
        FROM movimentacoes m JOIN produtos p ON m.produto_id = p.id
        WHERE 1=1
    """
    params = []

    if tipo:
        query += " AND m.tipo=?"
        params.append(tipo)
    if data_de:
        query += " AND date(m.data) >= ?"
        params.append(data_de)
    if data_ate:
        query += " AND date(m.data) <= ?"
        params.append(data_ate)
    if produto_id:
        query += " AND m.produto_id=?"
        params.append(int(produto_id))

    query += " ORDER BY m.data DESC LIMIT 200"
    movimentacoes = db.execute(query, params).fetchall()
    produtos = db.execute(
        "SELECT id, nome, sku FROM produtos WHERE ativo=1 ORDER BY nome"
    ).fetchall()

    return render_template("movimentacoes.html",
        movimentacoes=movimentacoes,
        produtos=produtos,
        tipo=tipo, data_de=data_de, data_ate=data_ate, produto_id=produto_id,
    )


@app.route("/movimentacoes/nova", methods=["GET", "POST"])
def movimentacao_nova():
    db = get_db()
    if request.method == "POST":
        try:
            produto_id = int(request.form["produto_id"])
            tipo = request.form["tipo"]
            quantidade = int(request.form["quantidade"])
            observacao = request.form.get("observacao", "")

            if quantidade <= 0:
                flash("A quantidade deve ser maior que zero.", "danger")
                raise ValueError("qty <= 0")

            produto = db.execute(
                "SELECT * FROM produtos WHERE id=? AND ativo=1", (produto_id,)
            ).fetchone()
            if not produto:
                flash("Produto não encontrado.", "danger")
                raise ValueError("produto not found")

            if tipo == "saida" and produto["estoque_atual"] < quantidade:
                flash(
                    f"Estoque insuficiente. Disponível: {produto['estoque_atual']} un.",
                    "danger"
                )
                raise ValueError("estoque insuficiente")

            db.execute("""
                INSERT INTO movimentacoes (produto_id, tipo, quantidade, observacao)
                VALUES (?, ?, ?, ?)
            """, (produto_id, tipo, quantidade, observacao))

            if tipo == "entrada":
                db.execute(
                    "UPDATE produtos SET estoque_atual = estoque_atual + ? WHERE id=?",
                    (quantidade, produto_id)
                )
            else:
                db.execute(
                    "UPDATE produtos SET estoque_atual = estoque_atual - ? WHERE id=?",
                    (quantidade, produto_id)
                )

            db.commit()
            flash(
                f"{'Entrada' if tipo == 'entrada' else 'Saída'} de {quantidade} un. registrada!",
                "success"
            )
            return redirect(url_for("movimentacoes_lista"))

        except ValueError:
            pass
        except Exception as e:
            flash(f"Erro: {e}", "danger")

    produtos = db.execute(
        "SELECT id, nome, sku, estoque_atual FROM produtos WHERE ativo=1 ORDER BY nome"
    ).fetchall()
    return render_template("movimentacao_form.html", produtos=produtos)


# ──────────────────────────────────────────────
#  ALERTAS
# ──────────────────────────────────────────────

@app.route("/alertas")
def alertas():
    db = get_db()
    produtos = db.execute("""
        SELECT p.*, c.nome as categoria_nome,
               (p.estoque_minimo - p.estoque_atual) as deficit,
               ROUND(p.estoque_atual * 100.0 / MAX(p.estoque_minimo, 1), 1) as pct
        FROM produtos p JOIN categorias c ON p.categoria_id = c.id
        WHERE p.ativo=1 AND p.estoque_atual < p.estoque_minimo
        ORDER BY pct ASC
    """).fetchall()
    return render_template("alertas.html", produtos=produtos)


# ──────────────────────────────────────────────
#  RELATÓRIOS
# ──────────────────────────────────────────────

@app.route("/relatorios")
def relatorios():
    db = get_db()

    # Valor em estoque por categoria
    por_categoria = db.execute("""
        SELECT c.nome,
               COUNT(p.id) as qtd_produtos,
               COALESCE(SUM(p.estoque_atual), 0) as total_unidades,
               COALESCE(SUM(p.estoque_atual * p.preco_custo), 0) as valor_custo,
               COALESCE(SUM(p.estoque_atual * p.preco_venda), 0) as valor_venda
        FROM categorias c LEFT JOIN produtos p ON p.categoria_id = c.id AND p.ativo=1
        GROUP BY c.id ORDER BY valor_custo DESC
    """).fetchall()

    # Produtos sem movimentação há 30+ dias
    trinta_dias = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    sem_movimento = db.execute("""
        SELECT p.nome, p.sku, c.nome as categoria_nome,
               p.estoque_atual, p.preco_custo,
               (p.estoque_atual * p.preco_custo) as valor_parado,
               MAX(m.data) as ultima_mov
        FROM produtos p
        JOIN categorias c ON p.categoria_id = c.id
        LEFT JOIN movimentacoes m ON m.produto_id = p.id
        WHERE p.ativo=1
        GROUP BY p.id
        HAVING ultima_mov IS NULL OR date(ultima_mov) < ?
        ORDER BY valor_parado DESC
    """, (trinta_dias,)).fetchall()

    # Movimentações por período (últimos 30 dias agrupados por semana)
    mov_periodo = db.execute("""
        SELECT
            strftime('%W', data) as semana,
            MIN(date(data)) as inicio,
            MAX(date(data)) as fim,
            SUM(CASE WHEN tipo='entrada' THEN quantidade ELSE 0 END) as entradas,
            SUM(CASE WHEN tipo='saida' THEN quantidade ELSE 0 END) as saidas,
            COUNT(*) as total_mov
        FROM movimentacoes
        WHERE date(data) >= date('now', '-30 days')
        GROUP BY semana ORDER BY semana DESC
    """).fetchall()

    # Top 10 produtos mais movimentados
    top_movimentados = [
        dict(row) for row in db.execute("""
        SELECT p.nome, p.sku,
               SUM(m.quantidade) as total_mov,
               SUM(CASE WHEN m.tipo='entrada' THEN m.quantidade ELSE 0 END) as entradas,
               SUM(CASE WHEN m.tipo='saida' THEN m.quantidade ELSE 0 END) as saidas
        FROM movimentacoes m JOIN produtos p ON m.produto_id = p.id
        WHERE date(m.data) >= date('now', '-30 days')
        GROUP BY p.id ORDER BY total_mov DESC LIMIT 10
    """).fetchall()
    ]

    return render_template("relatorios.html",
        por_categoria=por_categoria,
        sem_movimento=sem_movimento,
        mov_periodo=mov_periodo,
        top_movimentados=top_movimentados,
    )


# ──────────────────────────────────────────────
#  API JSON (para gráficos dinâmicos)
# ──────────────────────────────────────────────

@app.route("/api/dashboard-data")
def api_dashboard():
    db = get_db()
    dados_7d = []
    for i in range(6, -1, -1):
        dia = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        label = (datetime.now() - timedelta(days=i)).strftime("%d/%m")
        row = db.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN tipo='entrada' THEN quantidade ELSE 0 END), 0) as entradas,
                COALESCE(SUM(CASE WHEN tipo='saida' THEN quantidade ELSE 0 END), 0) as saidas
            FROM movimentacoes WHERE date(data)=?
        """, (dia,)).fetchone()
        dados_7d.append({
            "label": label, "entradas": row["entradas"], "saidas": row["saidas"]
        })
    return jsonify(dados_7d)


# ──────────────────────────────────────────────
#  STARTUP
# ──────────────────────────────────────────────

if __name__ == "__main__":
    init_db()

    # Seed demo data if DB is empty
    db_check = sqlite3.connect(DATABASE)
    count = db_check.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
    db_check.close()
    if count == 0:
        from seed import seed_demo_data
        seed_demo_data(DATABASE)
        print("Dados de demonstracao inseridos com sucesso.")
    atualizar_datas_demo()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "0") == "1")
