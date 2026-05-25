# Como Rodar os Projetos Localmente

Guia para executar cada projeto do portfólio Base Exata durante o desenvolvimento e testes.

---

## Pré-requisitos

- Python 3.x instalado
- pip disponível no PATH
- Virtualenv (opcional, mas recomendado para isolar dependências)

---

## Instruções gerais

- Cada projeto é totalmente independente — banco, dependências e servidor separados
- Todos rodam em `http://localhost:5000` — execute **um projeto por vez** localmente
- O banco SQLite (`database.db`) é criado e populado com dados demo automaticamente na primeira execução
- `database.db` não é versionado — é descartável

---

## Projeto 1 — Dashboard de Inteligência de Vendas

```bash
cd projeto-1-vendas

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

Acesse: http://localhost:5000

**Seed automático:** na primeira execução, o banco é criado e os dados demo são populados automaticamente. Nenhuma ação manual necessária.

**Resetar dados demo:**
```bash
del database.db
python app.py
```

---

## Projeto 2 — Sistema de Gestão de Estoque

```bash
cd projeto-2-estoque

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

Acesse: http://localhost:5000

**Seed automático:** na primeira execução, o banco é criado e os dados demo são populados automaticamente. Nenhuma ação manual necessária.

**Resetar dados demo:**
```bash
del database.db
python app.py
```

---

## Projeto 3 — Monitor de Eficiência Industrial OEE

Em desenvolvimento.

---

## Projeto 4 — Automação de Relatórios

Em desenvolvimento.

---

## Projeto 5 — Análise de Sazonalidade e Demanda

Em desenvolvimento.

---

## Projeto 6 — Painel de Performance Comercial

Em desenvolvimento.

---

## Observações

- **`database.db` não é versionado** — o arquivo é gerado automaticamente e está no `.gitignore` de cada projeto
- **Rodar um projeto por vez** — todos usam a porta 5000; para rodar dois simultaneamente, altere a porta em `app.run(port=XXXX)`
- **Testar responsividade:** redimensione o navegador para 375px (mobile) e 1440px (desktop), ou use o DevTools (F12 → Toggle device toolbar)
- **Dependências:** Flask 3.0.3 + Gunicorn 21.2.0 — sem npm, sem node, sem tooling de frontend
