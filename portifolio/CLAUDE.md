# Base Exata — Portfólio de Micro-Aplicações

## Objetivo

Portfólio de 6 micro-aplicações web standalone representando os serviços reais da consultoria **Base Exata** (análise de dados e automação para comércio, supermercados e pequenas indústrias de Capivari, SP). Cada aplicação é exibida via iframe no site principal da consultoria.

---

## Stack Técnica

- **Linguagem:** Python 3.x
- **Framework:** Flask
- **Frontend:** Bootstrap 5 (CDN) + Chart.js (CDN) — sem npm, sem node
- **Banco de dados:** SQLite (um arquivo `database.db` por projeto, gerado automaticamente)
- **Servidor de produção:** Gunicorn
- **Deploy:** Render free tier
- **Autenticação:** nenhuma — projetos públicos demo

---

## Os 6 Projetos

| Pasta | Nome | Observação |
|---|---|---|
| `projeto-1-vendas/` | Dashboard de Inteligência de Vendas | Flask + Chart.js + SQLite |
| `estoque-app/` | Sistema de Gestão de Estoque | **Referência oficial de estoque** |
| `projeto-3-oee/` | Monitor de Eficiência Industrial OEE | Dark theme |
| `projeto-4-relatorios/` | Automação de Relatórios | Flask + Bootstrap 5 + Chart.js |
| `projeto-5-sazonalidade/` | Análise de Sazonalidade e Demanda | Flask + Chart.js + SQLite |
| `projeto-6-performance/` | Painel de Performance Comercial | Flask + Chart.js + Bootstrap 5 |

### Ordem de implementação obrigatória

1. `estoque-app` — serve como referência estrutural oficial do sistema de estoque
2. `projeto-1-vendas`
3. `projeto-3-oee`
4. `projeto-4-relatorios`
5. `projeto-5-sazonalidade`
6. `projeto-6-performance`

---

## Estrutura de Pastas (replicar para cada projeto)

```
projeto-X/
├── app.py                # aplicação Flask principal
├── requirements.txt      # dependências com versões fixadas
├── Procfile              # conteúdo: web: gunicorn app:app
├── seed_data.py          # script de população de dados demo
├── templates/
│   ├── base.html         # navbar, banner demo, footer, imports CDN (Bootstrap + Chart.js)
│   └── index.html        # herda base.html
├── static/
│   ├── css/style.css
│   └── js/main.js
└── database.db           # gerado automaticamente no startup (não versionar)
```

---

## Requisitos Obrigatórios (todos os projetos)

- **Banner demo fixo no topo** em todos os templates:
  `MODO DEMONSTRACAO — Projeto Vitrine | Base Exata`
- **Seed automático no startup:** se o banco estiver vazio, `seed_data.py` é chamado automaticamente em `app.py` (antes do primeiro request ou no `create_app`)
- **Responsivo:** compatível de 375px (mobile) até 1440px (desktop)
- **Todas as libs via CDN** — Bootstrap 5, Chart.js, qualquer outra lib JS/CSS
- **`requirements.txt` com versões fixadas** (ex: `Flask==3.0.3`, `gunicorn==22.0.0`)
- **Sem tela de login** — acesso direto ao dashboard

---

## Convenções de Código

- Comentários e docstrings em **PT-BR**
- Variáveis e funções Python em **snake_case**
- Dados demo **realistas para o contexto de supermercado, varejo e indústria** de interior de SP (nomes de produtos, fornecedores, SKUs, turnos industriais, etc.)
- Código simples e direto — sem abstrações desnecessárias
- Cada projeto é **totalmente independente**: sem imports entre projetos, sem banco compartilhado

---

## Banco de Dados

- **Engine:** SQLite
- **Arquivo:** `database.db` na raiz de cada projeto
- Criado automaticamente pelo Flask na primeira execução
- `database.db` deve estar no `.gitignore` de cada projeto (arquivo gerado/descartável)
- O seed popula dados suficientes para que os gráficos sejam visualmente representativos

---

## Integrações Externas

Nenhuma API externa. Todos os dados são gerados pelo `seed_data.py` local.

CDNs usadas (apenas leitura, sem chave):
- Bootstrap 5: `https://cdn.jsdelivr.net/npm/bootstrap@5`
- Chart.js: `https://cdn.jsdelivr.net/npm/chart.js`

---

## Regras Importantes

- **Nunca conectar ao banco Oracle corporativo** — este projeto não tem relação com o ambiente corporativo
- **Nunca instalar dependências pesadas no disco C** — Render cuida do ambiente de produção; localmente só Flask + Gunicorn
- **Não compartilhar banco entre projetos** — cada `database.db` é isolado
- **Não adicionar autenticação** — os projetos são demos públicos
- **Não usar npm/node/webpack** — todo JS via CDN, zero tooling de frontend
- **Não versionar `database.db`** — arquivo deve estar no `.gitignore`
- **Manter `requirements.txt` com versões fixadas** — evitar quebras no Render

---

## Como Rodar Localmente

```bash
# Dentro da pasta de um projeto específico
cd ..\estoque-app

pip install -r requirements.txt
python app.py
# Acesse http://localhost:5000
```

O seed roda automaticamente se o banco estiver vazio.

---

## Como Fazer Deploy (Render)

Cada projeto é um serviço separado no Render:
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:app` (definido no `Procfile`)
- **Environment:** Python

---

## Como Testar

Sem suite de testes automatizados por enquanto. Validação manual:
1. Executar `python app.py` localmente
2. Verificar se o banco foi criado e populado com seed
3. Verificar se os gráficos renderizam corretamente
4. Testar responsividade em 375px e 1440px

---

## Proximas Features Planejadas

- [ ] Completar os 6 projetos na ordem definida
- [ ] Validar exibição via iframe no site principal da Base Exata
- [ ] Ajustar paleta de cores e identidade visual por projeto (projeto-3 usa dark theme)
- [ ] Revisar dados de seed para maior realismo regional (Capivari, SP)
