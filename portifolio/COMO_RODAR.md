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
- O sistema de estoque oficial fica fora da pasta `portifolio`, em `estoque-app/`
- Os dados demonstrativos usam datas relativas e são atualizados automaticamente para manter dashboards recentes em ambientes de demo.

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

## Projeto 3 — Monitor de Eficiência Industrial OEE

```bash
cd projeto-3-oee

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

## Projeto 4 — Automação de Relatórios

```bash
cd projeto-4-relatorios

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

## Projeto 5 — Análise de Sazonalidade e Demanda

```bash
cd projeto-5-sazonalidade

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

## Projeto 6 — Painel de Performance Comercial

```bash
cd projeto-6-performance

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

## Sistema de Gestão de Estoque Oficial

O sistema de estoque oficial da Base Exata não fica em `portifolio/`. Use a pasta `estoque-app/`.

```bash
cd ../estoque-app

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

## Observações

- **`database.db` não é versionado** — o arquivo é gerado automaticamente e está no `.gitignore` de cada projeto
- **Rodar um projeto por vez** — todos usam a porta 5000; para rodar dois simultaneamente, altere a porta em `app.run(port=XXXX)`
- **Testar responsividade:** redimensione o navegador para 375px (mobile) e 1440px (desktop), ou use o DevTools (F12 → Toggle device toolbar)
- **Dependências:** Flask 3.0.3 + Gunicorn 21.2.0 — sem npm, sem node, sem tooling de frontend
