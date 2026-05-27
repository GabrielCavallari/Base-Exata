# Sessões de Implementação — projeto-4-relatorios
# Gerado em: 2026-04-08
# Objetivo: implementar projeto-4-relatorios (Automação de Relatórios)

---

## Estado atual

| Módulo | Status | O que falta |
|--------|--------|-------------|
| `estoque-app` | Completo (referência oficial) | — |
| `projeto-3-oee` | Completo | — |
| `projeto-4-relatorios` | Pendente | Pasta não existe, todos os arquivos faltam |

---

## Sessões geradas

| # | Agente | Objetivo | Dependência |
|---|--------|----------|-------------|
| A | backend-architect | Backend Flask + SQLite + seed para projeto-4-relatorios | independente |
| B | frontend-developer | Templates HTML/CSS/JS (fundo claro) para projeto-4-relatorios | aguardar Sessão A |
| C | code-reviewer | Revisar projeto-4-relatorios completo | aguardar Sessões A e B |

Sessão B depende da Sessão A: o frontend-developer precisa ler o app.py pronto
para conhecer as rotas exatas antes de criar qualquer arquivo.

---

## Sessão A — backend-architect (independente)

Você é o backend-architect. Crie todos os arquivos do backend do projeto-4-relatorios
dentro de C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-4-relatorios/

Antes de começar, leia os dois arquivos abaixo para entender o padrão do portfólio:
- C:/Users/Gabriel/Documents/Base Exata/estoque-app/app.py
- C:/Users/Gabriel/Documents/Base Exata/estoque-app/seed.py

Replique exatamente o mesmo padrão estrutural desses arquivos. Não invente variações.

---

CONTEXTO DO PROJETO

Este é o quarto projeto de um portfólio de 6 micro-aplicações Flask para a consultoria
Base Exata (Capivari, SP). Cada projeto é totalmente independente: banco próprio, sem
imports entre projetos.

O projeto-4-relatorios simula uma "Automação de Relatórios Gerenciais" para um
supermercado/varejista de médio porte do interior de SP. O dashboard exibe relatórios
que antes eram feitos manualmente no Excel: fechamento mensal de vendas por categoria,
ranking de fornecedores por volume de compra, e evolução do ticket médio mensal.
Os dados são demo — gerados pelo seed, sem input do usuário.

---

ARQUIVO: app.py

Siga exatamente o padrão do estoque-app/app.py:
- Cabeçalho: "# Projeto 4 — Automação de Relatórios\n# Base Exata | Flask + SQLite"
- Importações: sqlite3, os, datetime/timedelta, Flask/render_template/jsonify
- BASE_DIR = os.path.dirname(os.path.abspath(__file__))
- DATABASE = os.path.join(BASE_DIR, 'database.db')
- Funções: get_db(), criar_tabelas(), banco_vazio(), inicializar_banco()
- Chamada de inicializar_banco() no nível do módulo (após definição, antes das rotas)
- banco_vazio() verifica COUNT(*) na tabela vendas
- inicializar_banco() chama criar_tabelas() e, se vazio, importa e chama seed_database(DATABASE) de seed_data.py
- if __name__ == '__main__': app.run(debug=True)

Tabelas a criar em criar_tabelas() via conn.executescript():

  categorias:
    id INTEGER PRIMARY KEY
    nome TEXT NOT NULL
    margem_media REAL NOT NULL    -- margem percentual média da categoria, ex: 0.28 para 28%

  fornecedores:
    id INTEGER PRIMARY KEY
    nome TEXT NOT NULL
    cidade TEXT NOT NULL
    categoria_id INTEGER           -- categoria principal deste fornecedor
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)

  vendas:
    id INTEGER PRIMARY KEY
    data TEXT NOT NULL             -- formato YYYY-MM-DD
    categoria_id INTEGER NOT NULL
    fornecedor_id INTEGER NOT NULL
    quantidade_itens INTEGER NOT NULL
    valor_total REAL NOT NULL      -- valor bruto da venda no dia para aquela categoria/fornecedor
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)

  ticket_diario:
    id INTEGER PRIMARY KEY
    data TEXT NOT NULL             -- formato YYYY-MM-DD
    num_transacoes INTEGER NOT NULL -- numero de transacoes no dia
    ticket_medio REAL NOT NULL     -- valor medio por transacao no dia

Rotas Flask:

  GET /
    Renderiza templates/index.html sem variáveis de contexto.
    Todos os dados vêm via fetch JS nas rotas /api/*.

  GET /api/resumo
    Retorna JSON com 4 KPIs calculados sobre todos os dados do banco:
      {
        "total_vendas": float,           -- soma de valor_total em todas as vendas
        "ticket_medio": float,           -- media de ticket_medio em ticket_diario
        "categorias_ativas": int,        -- contagem de categorias com ao menos 1 venda
        "fornecedores_ativos": int       -- contagem de fornecedores com ao menos 1 venda
      }
    Proteger divisão por zero: se COUNT(*) de ticket_diario == 0, retornar ticket_medio: 0.0
    Retornar total_vendas arredondado em 2 casas decimais.
    Retornar ticket_medio arredondado em 2 casas decimais.

  GET /api/vendas-por-categoria
    Retorna lista JSON: [{nome, total, percentual}]
    Para cada categoria, somar valor_total de todas as vendas associadas.
    percentual = total_categoria / total_geral * 100, arredondado em 1 casa decimal.
    total arredondado em 2 casas decimais.
    Ordenar por total DESC.
    Exemplo de retorno: [{"nome": "Bebidas", "total": 48320.50, "percentual": 22.3}, ...]

  GET /api/ranking-fornecedores
    Retorna lista JSON com os top 10 fornecedores por volume de compra:
      [{nome, cidade, total_compras, num_pedidos}]
    total_compras = soma de valor_total das vendas deste fornecedor, arredondado em 2 casas.
    num_pedidos = contagem de registros de vendas deste fornecedor.
    Ordenar por total_compras DESC.
    Retornar no máximo 10 itens.

  GET /api/evolucao-ticket
    Retorna lista JSON: [{mes, ticket_medio}]
    Agrupar ticket_diario por mês (extrair YYYY-MM do campo data).
    Para cada mês, calcular a média de ticket_medio dos dias daquele mês.
    mes no formato "MMM/AA" em português, ex: "Jan/24", "Fev/24", ..., "Dez/24"
    Ordenar por data ASC (do mais antigo para o mais recente).
    ticket_medio arredondado em 2 casas decimais.
    Gerar os últimos 12 meses a partir da data atual.
    Se não houver registro para um mês, não incluir na lista.

  GET /api/fechamento-mensal
    Retorna lista JSON com fechamento dos últimos 12 meses:
      [{mes, total_vendas, margem_estimada}]
    mes no formato "MMM/AA" em português.
    total_vendas = soma de valor_total das vendas daquele mês, arredondado em 2 casas.
    margem_estimada = soma de (valor_total * margem_media_da_categoria) para cada venda
                      no mês, arredondado em 2 casas.
    Para calcular margem_estimada, fazer JOIN de vendas com categorias para obter margem_media.
    Ordenar por data ASC.
    Se não houver vendas em um mês, não incluir na lista.

---

ARQUIVO: seed_data.py

Função: seed_database(database_path)
  -- recebe o caminho do banco como argumento, igual ao padrão do projeto-2

Importações necessárias: sqlite3, random, from datetime import date, timedelta

Categorias (inserir 8):
  Nome                | margem_media
  "Hortifruti"        | 0.35
  "Bebidas"           | 0.28
  "Padaria"           | 0.42
  "Carnes e Aves"     | 0.22
  "Laticínios"        | 0.30
  "Higiene Pessoal"   | 0.38
  "Limpeza"           | 0.32
  "Mercearia"         | 0.25

Fornecedores (inserir 20):
  Distribuídos entre as 8 categorias (2 a 3 fornecedores por categoria).
  Nomes realistas para o interior de SP — usar nomes fictícios regionais. Exemplos:
    Hortifruti:       "Sítio São Benedito", "Hortifruti Capivari Ltda"
    Bebidas:          "Distribuidora Paulista de Bebidas", "Atacadão Bebidas Piracicaba", "Cooperativa Tietê"
    Padaria:          "Moinho Central Ltda", "Padaria Industrial Campinas"
    Carnes e Aves:    "Frigorífico Vale do Tietê", "Abatedouro São João da Boa Vista", "Aves do Interior"
    Laticínios:       "Laticínios Bela Vista", "Cooperativa Leite Capivari"
    Higiene Pessoal:  "Distribuidora Higiene SP", "Atacado Casa Limpa"
    Limpeza:          "Produtos Limpeza Sorocaba", "Distribuidora Lar Ltda"
    Mercearia:        "Atacadão Mercearia SP", "Distribuidora Central Interior", "Grãos & Cereais Ltda"
  Cidades: Capivari, Piracicaba, Campinas, Sorocaba, Rio Claro, São João da Boa Vista

Vendas:
  Período: últimos 12 meses completos a partir de hoje (date.today())
  Para cada dia do período:
    Gerar entre 4 e 8 registros de vendas (combinação categoria/fornecedor)
    Cada registro:
      quantidade_itens: inteiro entre 20 e 500
      valor_total: float entre 200.00 e 8000.00
      Variação realista: Bebidas e Mercearia com volumes maiores (até 8000),
      Hortifruti e Padaria com volumes menores (até 3000)
    Garantir que todos os 8 categorias apareçam ao longo dos dados
    Garantir que os top 3 fornecedores por volume sejam claramente maiores (2x o volume médio)
  Total aproximado de registros: 1500-2000 vendas

ticket_diario:
  Para cada dia dos últimos 12 meses:
    1 registro por dia
    num_transacoes: inteiro entre 180 e 450
    ticket_medio: float entre 38.00 e 95.00
    Variar ticket_medio com tendência de crescimento leve ao longo dos meses
    (meses mais recentes com ticket_medio ligeiramente maior)

Inserir na ordem: categorias → fornecedores (buscar IDs com SELECT após inserir) → vendas → ticket_diario
Commitar e fechar conexão ao final.

---

ARQUIVO: requirements.txt

Flask==3.0.3
gunicorn==22.0.0

---

ARQUIVO: Procfile

web: gunicorn app:app

---

ARQUIVO: .gitignore

database.db

---

CONVENÇÕES OBRIGATÓRIAS

- Comentários e docstrings em PT-BR
- snake_case em todas as variáveis e funções Python
- Sem abstrações desnecessárias — código simples e direto
- Sem autenticação, sem login
- Não criar templates HTML — isso é escopo da Sessão B
- Não instalar nenhuma dependência além de Flask e gunicorn
- Este projeto usa fundo claro (mesmo padrão do estoque-app) — não usar dark theme

---

## Sessão B — frontend-developer (abrir somente após Sessão A concluída)

Você é o frontend-developer. Crie todos os arquivos de frontend do projeto-4-relatorios
dentro de C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-4-relatorios/

OBRIGATÓRIO: leia os seguintes arquivos antes de criar qualquer arquivo:
1. C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-4-relatorios/app.py
   -- para conhecer as rotas /api/* exatas que o backend expõe
2. C:/Users/Gabriel/Documents/Base Exata/estoque-app/templates/base.html
   -- para entender o padrão de estrutura HTML e estilos inline do portfólio
3. C:/Users/Gabriel/Documents/Base Exata/estoque-app/templates/base.html
   -- para entender o padrão visual consolidado do sistema oficial de estoque

---

CONTEXTO DO PROJETO

Quarto projeto de um portfólio de 6 micro-aplicações Flask para a consultoria
Base Exata (Capivari, SP). O projeto-4-relatorios é um painel de "Automação de
Relatórios Gerenciais" para varejo — exibe dados que antes eram gerados manualmente
no Excel: fechamento mensal, ranking de fornecedores, ticket médio e vendas por categoria.

IMPORTANTE: este projeto usa fundo CLARO, igual ao estoque-app. Não usar dark theme.
Paleta: fundo #f4f6f9, navbar e elementos de destaque em #1a1a2e, acento em #e94560.

---

ARQUIVO: templates/base.html

Estrutura idêntica ao estoque-app/templates/base.html, com estas diferenças:

- Title block padrão: "Automação de Relatórios | Base Exata"
- CDNs (mesmas versões do projeto-2):
    Bootstrap 5.3.3: https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css
    Bootstrap Icons 1.11.3: https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css
    Chart.js 4.4.4: https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js
    Bootstrap JS 5.3.3: https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js
- Link para static/css/style.css via url_for
- Banner de demonstração obrigatório (div com classe banner-demo, antes da navbar):
    MODO DEMONSTRACAO — Projeto Vitrine | Base Exata
- Navbar com classes "navbar navbar-expand-lg navbar-dark navbar-custom":
    Brand: ícone bi-file-earmark-bar-graph + "Base Exata — Relatórios"
    Apenas um link de nav: Dashboard (href="/", ativo sempre)
- main.container.py-4 com {% block content %}
- Footer com classe footer-custom:
    "Base Exata © 2024 — Análise de Dados e Automação para Varejo e Indústria"
- Script Chart.js e Bootstrap JS via CDN antes do main.js
- Script link para static/js/main.js via url_for
- {% block scripts %} após o main.js

---

ARQUIVO: templates/index.html

Herda base.html. Toda a interação é via JavaScript (fetch das rotas /api/*).
Não usar variáveis Jinja2 de contexto — a rota GET / não passa variáveis.

Seção 1 — Narrativa do case (div com classe case-destaque, mb-4):
  Ícone bi-trophy-fill + texto:
  "Case real: Reduziu de 6 horas para 12 minutos o tempo de geração do fechamento
  mensal de uma rede varejista de Capivari, integrando dados de 3 planilhas distintas."

Seção 2 — 4 cards KPI em linha (row g-3 mb-4, col-6 col-md-3):
  Card 1: id="kpi-total-vendas"       | ícone bi-currency-dollar | label "Total de Vendas"
  Card 2: id="kpi-ticket-medio"       | ícone bi-receipt          | label "Ticket Médio"
  Card 3: id="kpi-categorias"         | ícone bi-tags             | label "Categorias Ativas"
  Card 4: id="kpi-fornecedores"       | ícone bi-truck            | label "Fornecedores Ativos"
  Cada card tem:
    div.kpi-icon (ícone)
    div.kpi-valor com id correspondente (ex: id="valor-total-vendas")
    div.kpi-label com o texto do label
  Valores preenchidos via JavaScript com fetch('/api/resumo')

Seção 3 — Dois gráficos lado a lado (row g-3 mb-4):
  Col esquerda (col-12 col-lg-7): gráfico de rosca "Vendas por Categoria"
    canvas id="graficoVendasCategoria"
    Card com card-header-custom e ícone bi-pie-chart
  Col direita (col-12 col-lg-5): gráfico de barras vertical "Fechamento Mensal (12 meses)"
    canvas id="graficoFechamentoMensal"
    Card com card-header-custom e ícone bi-calendar-month
    Duas séries: "Total Vendas" (barras) e "Margem Estimada" (barras empilhadas ou linha)

Seção 4 — Gráfico de linha full-width (row g-3 mb-4):
  Col col-12: gráfico de linha "Evolução do Ticket Médio (12 meses)"
    canvas id="graficoTicket"
    Card com card-header-custom e ícone bi-graph-up-arrow

Seção 5 — Tabela de ranking de fornecedores (row g-3):
  Col col-12: tabela "Top 10 Fornecedores por Volume de Compras"
    Card com card-header-custom e ícone bi-award
    Tabela responsiva com colunas: # | Fornecedor | Cidade | Total Compras (R$) | N° Pedidos
    Thead com classe thead-custom
    Tbody id="tabelaFornecedores" — preenchido via JavaScript
    Coluna "#" exibe o número de posição (1 a 10)
    Coluna "Total Compras (R$)" formatada com R$ e separador de milhar

---

ARQUIVO: static/css/style.css

Fundo claro — mesmo padrão visual do estoque-app. Copiar e adaptar as mesmas
classes, apenas ajustando nomes de projeto e mantendo a paleta abaixo:

Paleta de variáveis CSS:
  --azul-escuro: #1a1a2e
  --vermelho-acento: #e94560
  --cinza-claro: #f4f6f9
  --texto-muted: #6c757d

body:
  background-color: var(--cinza-claro)
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif
  font-size: 14px

.banner-demo:
  background: var(--azul-escuro)
  color: var(--vermelho-acento)
  text-align: center
  padding: 8px 16px
  font-size: 13px
  font-weight: 600
  letter-spacing: 1px
  position: sticky
  top: 0
  z-index: 1050

.navbar-custom:
  background-color: var(--azul-escuro)
  box-shadow: 0 2px 8px rgba(0,0,0,0.3)

.navbar-custom .nav-link:hover,
.navbar-custom .nav-link.active:
  color: var(--vermelho-acento) !important

.kpi-card:
  border: none
  border-radius: 12px
  box-shadow: 0 2px 8px rgba(0,0,0,0.08)
  transition: transform 0.15s ease, box-shadow 0.15s ease

.kpi-card:hover:
  transform: translateY(-2px)
  box-shadow: 0 6px 16px rgba(0,0,0,0.12)

.kpi-icon: font-size: 2rem, color: var(--azul-escuro), margin-bottom: 8px
.kpi-valor: font-size: 1.6rem, font-weight: 700, color: var(--azul-escuro), line-height: 1.2
.kpi-label: font-size: 12px, color: var(--texto-muted), margin-top: 4px, text-transform: uppercase, letter-spacing: 0.5px

.card-header-custom:
  background-color: var(--azul-escuro)
  color: #fff
  border-radius: 8px 8px 0 0 !important

.thead-custom th:
  background-color: var(--azul-escuro)
  color: #fff
  font-weight: 500
  font-size: 13px
  text-transform: uppercase
  letter-spacing: 0.4px
  padding: 12px 16px
  border: none

.case-destaque:
  background: linear-gradient(135deg, var(--azul-escuro), #16213e)
  color: #fff
  border: none
  border-radius: 10px
  padding: 14px 20px
  font-size: 15px

.footer-custom:
  background-color: var(--azul-escuro)
  color: rgba(255,255,255,0.6)
  font-size: 12px

.badge-posicao:
  background-color: var(--azul-escuro)
  color: #fff
  font-size: 12px
  padding: 4px 8px
  border-radius: 4px

@media (max-width: 576px):
  .kpi-valor: font-size: 1.2rem
  .kpi-icon: font-size: 1.5rem
  .thead-custom th: font-size: 11px, padding: 8px 10px

---

ARQUIVO: static/js/main.js

Organizar em funções nomeadas, uma por responsabilidade. Inicializar tudo no DOMContentLoaded.
Comentários em PT-BR. Sem jQuery, sem frameworks — JS puro.

Função formatarMoeda(valor):
  -- recebe float, retorna string formatada como "R$ 1.234,56"
  -- usar Intl.NumberFormat('pt-BR', {style:'currency', currency:'BRL'})

Função carregarResumo():
  fetch('/api/resumo')
  Preencher id="valor-total-vendas" com formatarMoeda(data.total_vendas)
  Preencher id="valor-ticket-medio" com formatarMoeda(data.ticket_medio)
  Preencher id="valor-categorias" com data.categorias_ativas (número inteiro, sem formatação)
  Preencher id="valor-fornecedores" com data.fornecedores_ativos (número inteiro, sem formatação)

Função carregarVendasCategoria():
  fetch('/api/vendas-por-categoria')
  Renderizar gráfico de rosca no canvas "graficoVendasCategoria"
  Chart.js type: 'doughnut'
  Labels: array de data[i].nome
  Dados: array de data[i].total
  Cores distintas para cada fatia — usar paleta fixa de 8 cores:
    ['#1a1a2e','#e94560','#2d6a4f','#f4a261','#457b9d','#6d6875','#2a9d8f','#e76f51']
  Plugin legend: position 'right', labels com padding 12 e font-size 12
  Plugin tooltip: callback exibindo nome + formatarMoeda(value) + " (" + percentual + "%)"
    -- o percentual vem de data[i].percentual, não calculado no frontend
    -- para isso, guardar o array de data em variável acessível no tooltip callback
  cutout: '55%'

Função carregarFechamentoMensal():
  fetch('/api/fechamento-mensal')
  Renderizar gráfico de barras agrupadas no canvas "graficoFechamentoMensal"
  Chart.js type: 'bar'
  Labels: array de data[i].mes
  Dataset 1: label "Total Vendas", data: data[i].total_vendas
    backgroundColor: 'rgba(26, 26, 46, 0.8)'
    borderColor: '#1a1a2e'
    borderWidth: 1
  Dataset 2: label "Margem Estimada", data: data[i].margem_estimada
    backgroundColor: 'rgba(233, 69, 96, 0.7)'
    borderColor: '#e94560'
    borderWidth: 1
  Escala Y: beginAtZero true, ticks com prefixo "R$ " e sufixo "k" para valores em milhar
    -- usar callback: value => 'R$ ' + (value/1000).toFixed(0) + 'k'
  Plugin legend: display true, position 'top'
  Plugin tooltip: callback exibindo formatarMoeda(value)

Função carregarTicket():
  fetch('/api/evolucao-ticket')
  Renderizar gráfico de linha no canvas "graficoTicket"
  Chart.js type: 'line'
  Labels: array de data[i].mes
  Dataset: label "Ticket Médio (R$)", data: data[i].ticket_medio
  borderColor: '#e94560'
  backgroundColor: 'rgba(233, 69, 96, 0.08)'
  fill: true
  tension: 0.4
  pointRadius: 4
  pointBackgroundColor: '#1a1a2e'
  borderWidth: 2
  Escala Y: beginAtZero false, ticks com prefixo "R$ "
  Plugin legend: display false

Função carregarRankingFornecedores():
  fetch('/api/ranking-fornecedores')
  Para cada item na lista, criar uma <tr> no tbody "tabelaFornecedores":
    <td> com número de posição (índice + 1) usando span com classe badge-posicao
    <td> com item.nome
    <td> com item.cidade
    <td> com formatarMoeda(item.total_compras)
    <td> com item.num_pedidos

document.addEventListener('DOMContentLoaded', function() {
  carregarResumo();
  carregarVendasCategoria();
  carregarFechamentoMensal();
  carregarTicket();
  carregarRankingFornecedores();
});

---

CONVENÇÕES OBRIGATÓRIAS

- Comentários em PT-BR
- Nenhuma lib JS além das CDNs já declaradas no base.html (Bootstrap + Chart.js)
- Responsivo de 375px a 1440px
- Fundo CLARO em todos os elementos: body #f4f6f9, cards brancos, navbar e footer #1a1a2e
- Não criar ou modificar app.py, seed_data.py, requirements.txt ou Procfile
- Não usar npm, node, webpack ou qualquer tooling de frontend

---

## Sessão C — code-reviewer (abrir somente após Sessões A e B concluídas)

Você é o code-reviewer. Revise todos os arquivos criados nas Sessões A e B do projeto-4-relatorios.

Leia cada arquivo abaixo antes de emitir qualquer avaliação:
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-4-relatorios/app.py
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-4-relatorios/seed_data.py
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-4-relatorios/requirements.txt
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-4-relatorios/Procfile
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-4-relatorios/.gitignore
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-4-relatorios/templates/base.html
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-4-relatorios/templates/index.html
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-4-relatorios/static/css/style.css
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-4-relatorios/static/js/main.js

Verifique especificamente os seguintes pontos. Para cada ponto, informe: OK ou PROBLEMA (com descrição exata do que está errado e em qual linha/trecho).

BACKEND (app.py):

1. Divisão por zero protegida em todas as rotas:
   - /api/resumo: se não houver registros em ticket_diario, ticket_medio retorna 0.0
   - /api/vendas-por-categoria: se total_geral == 0, percentual retorna 0.0
   - /api/fechamento-mensal: se a categoria não tiver margem_media definida, não ocorre erro

2. /api/resumo retorna exatamente os 4 campos:
   total_vendas (float, 2 casas), ticket_medio (float, 2 casas),
   categorias_ativas (int), fornecedores_ativos (int)

3. /api/vendas-por-categoria retorna lista com campos nome, total, percentual
   ordenada por total DESC

4. /api/ranking-fornecedores retorna no máximo 10 itens com campos:
   nome, cidade, total_compras, num_pedidos — ordenados por total_compras DESC

5. /api/evolucao-ticket retorna lista com campos mes (formato "Mmm/AA" em português)
   e ticket_medio, ordenada ASC por data

6. /api/fechamento-mensal retorna lista com campos mes, total_vendas, margem_estimada
   ordenada ASC por data

7. inicializar_banco() é chamado no nível do módulo (não dentro de uma rota)

8. banco_vazio() verifica a tabela vendas (não outra tabela)

9. seed_data.py usa função seed_database(database_path) — este é o nome exato esperado

SEED (seed_data.py):

10. Seed insere exatamente 8 categorias com os nomes corretos:
    Hortifruti, Bebidas, Padaria, Carnes e Aves, Laticínios, Higiene Pessoal,
    Limpeza, Mercearia

11. Seed insere registros em ticket_diario para todos os dias do período
    (aproximadamente 365 registros)

12. O total de registros em vendas é suficiente para os gráficos renderizarem
    com dados visualmente representativos (mínimo de 300 registros)

FRONTEND (templates + static):

13. Banner "MODO DEMONSTRACAO — Projeto Vitrine | Base Exata" presente no base.html
    antes da navbar (não dentro dela)

14. Fundo claro: body usa background-color claro (#f4f6f9 ou similar),
    sem nenhum fundo escuro global no CSS (o dark deve ser apenas navbar, footer, banner)

15. Os 5 elementos JavaScript existem no index.html com os IDs corretos:
    canvas "graficoVendasCategoria", canvas "graficoFechamentoMensal",
    canvas "graficoTicket", tbody "tabelaFornecedores",
    e os 4 elementos id="valor-*" para os KPIs

16. JavaScript: todas as chamadas fetch apontam para as rotas corretas:
    /api/resumo, /api/vendas-por-categoria, /api/ranking-fornecedores,
    /api/evolucao-ticket, /api/fechamento-mensal

17. Função formatarMoeda presente e usando Intl.NumberFormat com locale pt-BR

18. Responsividade: col-6/col-md-3 nos KPIs, col-12/col-lg-* nos gráficos

19. Comentários e docstrings em PT-BR nos arquivos Python e JS

20. snake_case em todas as variáveis e funções Python

21. database.db presente no .gitignore

Formato de saída esperado:

Para cada item numerado acima, uma linha:
  [1] OK
  [2] PROBLEMA — <descrição exata com referência ao trecho do código>

Ao final, uma seção "Correções necessárias" listando apenas os itens com PROBLEMA
e a ação exata para corrigi-los.

Não modifique nenhum arquivo. Apenas reporte.
Não sugira melhorias além dos itens verificados acima.

---

## Observações finais

- **Sessão A** pode começar imediatamente — o backend não depende de nada.
- **Sessão B** só pode começar após a Sessão A terminar — o frontend-developer precisa ler o `app.py` pronto para conhecer as rotas exatas.
- **Sessão C** só pode começar após as duas anteriores concluírem.
- Não há paralelismo possível neste conjunto de três sessões.
