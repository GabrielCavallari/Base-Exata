# Sessões de Implementação — Projeto 5: Análise de Sazonalidade e Demanda
# Base Exata | Portfólio

---

## Estado atual

| Módulo | Status | O que falta |
|--------|--------|-------------|
| projeto-5-sazonalidade | Pendente | Tudo — pasta ainda não existe |

---

## Sessões geradas

| # | Agente | Objetivo | Dependência |
|---|--------|----------|-------------|
| A | backend-architect | app.py, seed_data.py, requirements.txt, Procfile | independente |
| B | frontend-developer | templates/ e static/ com Chart.js | aguardar Sessão A concluir |
| C | code-reviewer | revisão completa do projeto-5 | aguardar Sessões A e B concluírem |

Sessões A pode iniciar imediatamente. Sessão B só após Sessão A concluída. Sessão C só após Sessões A e B concluídas.

---

## Sessão A — backend-architect (independente)

```
Você é o backend-architect. Crie os seguintes arquivos em
C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-5-sazonalidade/

Leia C:/Users/Gabriel/Documents/Base Exata/portifólio/CLAUDE.md antes de começar.
Leia também C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-4-relatorios/app.py
e C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-3-oee/app.py
para entender o padrão de estrutura Flask usado no portfólio antes de escrever qualquer linha.

---

### app.py

Siga rigorosamente o mesmo padrão dos projetos de referência:
- Variável BASE_DIR com os.path.dirname(os.path.abspath(__file__))
- Variável DATABASE apontando para database.db na raiz do projeto
- Função get_db() com conn.row_factory = sqlite3.Row
- Função criar_tabelas() com conn.executescript(...)
- Função banco_vazio() verificando a tabela principal (vendas_diarias)
- Função inicializar_banco() chamando criar_tabelas() e seed se vazio
- Chamada a inicializar_banco() no nível do módulo (fora de qualquer rota)
- if __name__ == '__main__': app.run(debug=True) no final

Tabelas a criar (dentro do executescript):

  produtos (
      id INTEGER PRIMARY KEY,
      nome TEXT NOT NULL,
      categoria TEXT NOT NULL,
      unidade TEXT NOT NULL DEFAULT 'un'
  )

  vendas_diarias (
      id INTEGER PRIMARY KEY,
      produto_id INTEGER NOT NULL,
      data TEXT NOT NULL,
      quantidade INTEGER NOT NULL,
      valor_unitario REAL NOT NULL,
      FOREIGN KEY (produto_id) REFERENCES produtos(id)
  )

  previsoes (
      id INTEGER PRIMARY KEY,
      produto_id INTEGER NOT NULL,
      mes INTEGER NOT NULL,
      quantidade_prevista INTEGER NOT NULL,
      FOREIGN KEY (produto_id) REFERENCES produtos(id)
  )

Rotas Flask:

  GET /
    Renderiza templates/index.html.
    Não passa variáveis de contexto — o template busca dados via fetch JS.

  GET /api/resumo
    Retorna JSON:
    {
      "total_produtos": <int>,       -- COUNT de produtos
      "total_vendas_30d": <float>,   -- SUM(quantidade * valor_unitario) dos últimos 30 dias
      "ticket_medio_30d": <float>,   -- AVG diário de (SUM valor) nos últimos 30 dias, ou 0 se vazio
      "produto_mais_vendido": <str>  -- nome do produto com maior SUM(quantidade) nos últimos 30 dias
    }
    Use COALESCE para evitar None em campos numéricos.
    Proteção contra divisão por zero em ticket_medio_30d.

  GET /api/sazonalidade-mensal
    Retorna JSON: lista de 12 objetos, um por mês, do mês 1 ao 12.
    Cada objeto: { "mes": "Jan", "quantidade": <int>, "valor": <float> }
    Agrega SUM(quantidade) e SUM(quantidade * valor_unitario) de vendas_diarias
    agrupando por strftime('%m', data).
    Meses sem venda retornam quantidade: 0 e valor: 0.0.
    Mapeamento PT-BR: 1=Jan, 2=Fev, 3=Mar, 4=Abr, 5=Mai, 6=Jun,
                      7=Jul, 8=Ago, 9=Set, 10=Out, 11=Nov, 12=Dez.

  GET /api/top-produtos
    Retorna JSON: lista dos 8 produtos com maior SUM(quantidade) no período completo.
    Cada objeto: { "nome": <str>, "categoria": <str>, "quantidade_total": <int>, "valor_total": <float> }
    Ordenado por quantidade_total DESC.

  GET /api/evolucao-semanal
    Retorna JSON: lista das últimas 12 semanas, da mais antiga para a mais recente.
    Cada objeto: { "semana": "Sem 01/04", "quantidade": <int>, "valor": <float> }
    A label "semana" usa a data da segunda-feira da semana no formato "Sem DD/MM".
    Usa strftime('%W', data) para agrupar. Retorna somente semanas com registros.
    Limite: últimas 12 semanas a partir de hoje.

  GET /api/previsao-demanda
    Retorna JSON: lista dos produtos que têm previsão cadastrada.
    Cada objeto:
    {
      "produto": <str>,
      "categoria": <str>,
      "previsoes": [
        { "mes": "Jan", "previsto": <int> },
        ... (12 entradas, meses sem previsão retornam previsto: 0)
      ]
    }
    Agrupa por produto. Meses sem registro em previsoes retornam 0.

Todos os retornos JSON devem usar jsonify().
Comentários e docstrings em PT-BR.
Variáveis e funções em snake_case.

---

### seed_data.py

Crie a função seed_database(caminho_banco) que recebe o path absoluto do banco como argumento.
Segue o mesmo padrão dos projetos de referência: abre sqlite3.connect(caminho_banco), insere e faz commit, fecha.

Produtos a inserir (10 produtos, representativos de supermercado em Capivari, SP):
  id=1,  nome="Arroz Tipo 1 5kg",          categoria="Mercearia",    unidade="pc"
  id=2,  nome="Feijão Carioca 1kg",         categoria="Mercearia",    unidade="pc"
  id=3,  nome="Óleo de Soja 900ml",         categoria="Mercearia",    unidade="pc"
  id=4,  nome="Açúcar Cristal 5kg",         categoria="Mercearia",    unidade="pc"
  id=5,  nome="Cerveja Pilsen Lata 350ml",  categoria="Bebidas",      unidade="un"
  id=6,  nome="Refrigerante Cola 2L",       categoria="Bebidas",      unidade="un"
  id=7,  nome="Água Mineral 500ml",         categoria="Bebidas",      unidade="un"
  id=8,  nome="Frango Inteiro Kg",          categoria="Açougue",      unidade="kg"
  id=9,  nome="Sabão em Pó 1kg",            categoria="Limpeza",      unidade="pc"
  id=10, nome="Papel Higiênico 12 rolos",   categoria="Higiene",      unidade="pc"

Vendas diárias: gerar 730 registros (2 anos completos = 2023-04-08 até 2025-04-07).
Para cada dia, gerar 1 registro por produto, totalizando 10 registros/dia × 730 dias = 7.300 linhas.
Use from datetime import date, timedelta para gerar as datas.

Padrão de sazonalidade por produto (quantidade base diária e variação sazonal):
  - Arroz 5kg: base 45 un/dia. Pico em Jan-Fev (+30%), queda em Jun-Jul (-15%)
  - Feijão 1kg: base 38 un/dia. Pico em Jan-Mar (+25%), estável no restante
  - Óleo de Soja: base 30 un/dia. Pico em Jun-Ago (inverno, fritura, +20%), queda em Dez (-10%)
  - Açúcar 5kg: base 28 un/dia. Pico em Jun-Ago (festas juninas, +40%), queda em Jan-Fev (-10%)
  - Cerveja Lata: base 80 un/dia. Pico forte em Nov-Mar (verão/festas, +70%), vale em Jun-Ago (-40%)
  - Refrigerante 2L: base 60 un/dia. Pico em Nov-Mar (+50%), vale em Jun-Ago (-25%)
  - Água 500ml: base 120 un/dia. Pico em Dez-Mar (+60%), vale em Jun-Ago (-30%)
  - Frango Inteiro: base 55 un/dia. Pico em Jun-Jul (festa junina/inverno, +25%), estável no restante
  - Sabão em Pó: base 22 un/dia. Pico em Jan-Fev (+20%), sem vale significativo
  - Papel Higiênico: base 18 un/dia. Distribuição relativamente uniforme, leve pico em Jan (+10%)

Para cada dia, aplique o fator sazonal do mês correspondente multiplicado pela base.
Adicione variação aleatória de ±10% sobre o resultado final (use random.randint ou randrange).
Garanta que a quantidade seja sempre >= 1.

Valores unitários (fixos por produto, representativos de interior de SP em 2024):
  Arroz 5kg=R$24,90, Feijão 1kg=R$7,49, Óleo 900ml=R$5,99, Açúcar 5kg=R$18,90,
  Cerveja Lata=R$3,49, Refrigerante 2L=R$8,99, Água 500ml=R$1,49,
  Frango Inteiro=R$14,90, Sabão em Pó=R$9,99, Papel Higiênico=R$18,90

Previsões: inserir 1 linha por produto por mês (12 meses × 10 produtos = 120 linhas em previsoes).
Use o mesmo padrão sazonal descrito acima, calculando a quantidade mensal prevista como:
  base_diaria × fator_sazonal_do_mes × 30 (arredondado para int)
Mas apenas para os meses 1 a 12 (previsão anual genérica, sem ano específico).
Previsões representam a demanda esperada mensal para fins de planejamento de compras.

---

### requirements.txt

Flask==3.0.3
gunicorn==22.0.0

---

### Procfile

web: gunicorn app:app

---

Convenções obrigatórias:
- Comentários e docstrings em PT-BR
- Variáveis e funções em snake_case
- Sem abstrações desnecessárias
- Não criar templates, static, nem qualquer arquivo além dos listados acima
```

---

## Sessão B — frontend-developer (aguardar Sessão A concluir)

```
Você é o frontend-developer. Crie os seguintes arquivos em
C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-5-sazonalidade/

IMPORTANTE: Leia os arquivos abaixo antes de criar qualquer arquivo:
1. C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-5-sazonalidade/app.py
   — as rotas de API estão definidas lá; não invente endpoints
2. C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-2-estoque/templates/base.html
   — padrão de layout do portfólio (banner-demo, navbar, footer, CDN links)
3. C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-2-estoque/static/css/style.css
   — variáveis CSS e classes reutilizáveis (kpi-card, kpi-valor, card-header-custom, etc.)
4. C:/Users/Gabriel/Documents/Base Exata/portifólio/CLAUDE.md
   — regras do portfólio (sem npm/node, dark theme não se aplica aqui, CDN obrigatório)

---

### templates/base.html

Siga o mesmo padrão do projeto-2-estoque/templates/base.html com as seguintes adaptações:

- <html lang="pt-BR"> — sem data-bs-theme (este projeto usa tema claro como projeto-2 e projeto-4)
- <title>{% block title %}Sazonalidade e Demanda{% endblock %} | Base Exata</title>
- CDNs obrigatórias (mesmas versões do projeto-2):
    Bootstrap 5.3.3 CSS: https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css
    Bootstrap Icons 1.11.3: https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css
    Bootstrap 5.3.3 JS: https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js
    Chart.js 4.4.4: https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js
- Link para static/css/style.css via url_for
- Banner demo obrigatório (exatamente como no projeto-2, com classe banner-demo):
    <div class="banner-demo">
        MODO DEMONSTRACAO — Projeto Vitrine | Base Exata
    </div>
- Navbar com classe navbar-custom e navbar-dark:
    Brand: <i class="bi bi-graph-up-arrow me-2"></i>Base Exata — Sazonalidade
    Links: Dashboard (/) — sem outras páginas neste projeto
- <main class="container py-4">{% block content %}{% endblock %}</main>
- Footer com classe footer-custom:
    Base Exata &copy; 2024 — Análise de Dados e Automação para Varejo e Indústria
- Script src para static/js/main.js via url_for
- {% block scripts %}{% endblock %} após o script de main.js

---

### templates/index.html

Herda base.html ({% extends 'base.html' %}).

Seção 1 — Título da página:
  <h5 class="mb-4"><i class="bi bi-bar-chart-line me-2"></i>Análise de Sazonalidade e Demanda</h5>

Seção 2 — 4 cards de KPI em linha (usa as classes kpi-card, kpi-valor, kpi-label, kpi-icon do style.css):
  Card 1: id="kpi-total-produtos"  | ícone bi-box-seam    | label "Total de Produtos"
  Card 2: id="kpi-vendas-30d"      | ícone bi-currency-dollar | label "Vendas (30 dias)"  | valor formatado como R$ X.XXX,XX
  Card 3: id="kpi-ticket-30d"      | ícone bi-receipt     | label "Ticket Médio/Dia"   | valor formatado como R$ X.XXX,XX
  Card 4: id="kpi-mais-vendido"    | ícone bi-trophy      | label "Mais Vendido (30d)"
  Dados preenchidos por JS via GET /api/resumo.
  Layout: row com 4 colunas (col-6 col-md-3).

Seção 3 — Gráfico de barras: Sazonalidade Mensal (quantidade vendida por mês)
  Card com header "Sazonalidade Mensal — Quantidade Vendida" (classe card-header-custom)
  <canvas id="grafico-sazonalidade" height="100">
  Dados de GET /api/sazonalidade-mensal.
  Tipo: 'bar', eixo X = mes, eixo Y = quantidade.
  Título do eixo Y: "Quantidade (unidades)".

Seção 4 — Dois gráficos lado a lado em tela >= md (col-12 col-md-6):
  Coluna esquerda — Gráfico de linha: Evolução Semanal (últimas 12 semanas)
    Card com header "Evolução Semanal — Últimas 12 Semanas" (classe card-header-custom)
    <canvas id="grafico-semanal" height="160">
    Dados de GET /api/evolucao-semanal.
    Tipo: 'line', eixo X = semana, eixo Y = valor (R$).
    Linha com tension: 0.3, sem fill.

  Coluna direita — Gráfico de rosca: Top 8 Produtos por Volume
    Card com header "Top 8 Produtos — Volume Total" (classe card-header-custom)
    <canvas id="grafico-top-produtos" height="160">
    Dados de GET /api/top-produtos.
    Tipo: 'doughnut', labels = nome, data = quantidade_total.
    Legenda posicionada abaixo (position: 'bottom').

Seção 5 — Tabela: Previsão de Demanda Mensal
  Card com header "Previsão de Demanda Mensal por Produto" (classe card-header-custom)
  Tabela responsiva (table-responsive) com thead classe thead-custom:
    Colunas: Produto | Categoria | Jan | Fev | Mar | Abr | Mai | Jun | Jul | Ago | Set | Out | Nov | Dez
  Corpo da tabela preenchido por JS via GET /api/previsao-demanda.
  Cada célula de mês exibe o valor inteiro (quantidade prevista).
  Sem cores condicionais — tabela simples e legível.
  Zebra: table-striped.

---

### static/css/style.css

Copie integralmente as variáveis e classes do projeto-2-estoque/static/css/style.css
(todas as classes: .banner-demo, .navbar-custom, .kpi-card, .kpi-icon, .kpi-valor, .kpi-label,
.card-header-custom, .thead-custom, .footer-custom e o bloco @media (max-width: 576px)).

Adicione ao final (sem remover nada do original):

  /* Projeto 5 — Sazonalidade */
  .grafico-container {
      position: relative;
      min-height: 200px;
  }

  .tabela-previsao td {
      text-align: center;
      font-size: 13px;
      padding: 6px 10px;
  }

  .tabela-previsao th:first-child,
  .tabela-previsao td:first-child {
      text-align: left;
      min-width: 160px;
  }

---

### static/js/main.js

Organização: uma função assíncrona por endpoint, todas chamadas no DOMContentLoaded.
Sem frameworks — fetch puro.

Função carregarResumo():
  GET /api/resumo
  Preenche:
    document.getElementById('kpi-total-produtos').textContent = data.total_produtos
    document.getElementById('kpi-vendas-30d').textContent = formatarReais(data.total_vendas_30d)
    document.getElementById('kpi-ticket-30d').textContent = formatarReais(data.ticket_medio_30d)
    document.getElementById('kpi-mais-vendido').textContent = data.produto_mais_vendido

Função carregarSazonalidade():
  GET /api/sazonalidade-mensal
  Inicializa Chart.js tipo 'bar' no canvas id="grafico-sazonalidade":
    labels: array de data.map(d => d.mes)
    dataset único: quantidade, cor de preenchimento #1a1a2e (azul escuro do portfólio), sem borda visível

Função carregarSemanal():
  GET /api/evolucao-semanal
  Inicializa Chart.js tipo 'line' no canvas id="grafico-semanal":
    labels: array de data.map(d => d.semana)
    dataset único: valor (R$), cor da linha #e94560 (vermelho acento do portfólio)
    tension: 0.3, pointRadius: 3, sem fill

Função carregarTopProdutos():
  GET /api/top-produtos
  Inicializa Chart.js tipo 'doughnut' no canvas id="grafico-top-produtos":
    labels: data.map(d => d.nome)
    data: data.map(d => d.quantidade_total)
    Paleta de 8 cores: ['#1a1a2e','#e94560','#0f3460','#533483','#e94560','#16213e','#1a1a2e','#7c83fd']
    Use cores distintas — não repita a mesma cor nas primeiras 6 posições

Função carregarPrevisao():
  GET /api/previsao-demanda
  Preenche tbody da tabela com id="tbody-previsao":
    Para cada produto em data:
      Criar <tr> com: <td>produto.produto</td><td>produto.categoria</td>
      Seguido de 12 <td> com os valores de produto.previsoes[i].previsto (i=0..11)

Função auxiliar formatarReais(valor):
  Retorna string formatada como "R$ X.XXX,XX" usando
  valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

Todos os fetch com tratamento de erro: .catch(err => console.error('Erro ao carregar dados:', err))
Comentários em PT-BR.
Sem console.log de depuração além dos .catch.
Não criar rotas nem modificar app.py.
```

---

## Sessão C — code-reviewer (aguardar Sessões A e B concluírem)

```
Você é o code-reviewer. Revise todos os arquivos do projeto:
C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-5-sazonalidade/

Leia C:/Users/Gabriel/Documents/Base Exata/portifólio/CLAUDE.md antes de começar
para entender as regras obrigatórias do portfólio.

Liste os arquivos existentes antes de iniciar a revisão.

Verifique especificamente os seguintes pontos, reportando apenas problemas reais:

**app.py**
- Padrão de inicialização: BASE_DIR, DATABASE, get_db(), criar_tabelas(), banco_vazio(), inicializar_banco() chamado no nível do módulo
- Todas as 5 rotas existem: GET /, /api/resumo, /api/sazonalidade-mensal, /api/top-produtos, /api/evolucao-semanal, /api/previsao-demanda
- COALESCE em todos os SUM e AVG para evitar None
- Divisão por zero protegida em ticket_medio_30d e qualquer outra divisão
- Seed chamado com caminho absoluto (from seed_data import seed_database; seed_database(DATABASE))
- Comentários e docstrings em PT-BR
- Variáveis e funções em snake_case

**seed_data.py**
- Função seed_database(caminho_banco) recebe o path como argumento (não hardcoda o caminho)
- Gera dados para as 3 tabelas: produtos, vendas_diarias, previsoes
- Quantidade de registros coerente: ~7.300 em vendas_diarias (10 produtos × 730 dias), 120 em previsoes
- Sazonalidade visível nos dados (produtos de verão com pico em Dez-Mar, etc.)
- Importações usadas: sqlite3, datetime, random (ou equivalente)
- Sem hardcode de DATABASE — usa o argumento recebido

**templates/base.html**
- Banner MODO DEMONSTRACAO presente com classe banner-demo
- CDNs corretos: Bootstrap 5.3.3, Bootstrap Icons 1.11.3, Chart.js 4.4.4
- Tema claro (sem data-bs-theme="dark")
- {% block content %} e {% block scripts %} presentes
- Link para static/css/style.css e static/js/main.js via url_for

**templates/index.html**
- Herda base.html com {% extends 'base.html' %}
- 4 cards KPI com ids: kpi-total-produtos, kpi-vendas-30d, kpi-ticket-30d, kpi-mais-vendido
- Canvas com ids: grafico-sazonalidade, grafico-semanal, grafico-top-produtos
- Tabela com tbody id="tbody-previsao" e thead com 14 colunas (Produto, Categoria + 12 meses)
- Classes Bootstrap responsivas presentes (col-6 col-md-3 nos KPIs, col-12 col-md-6 nos gráficos lado a lado)

**static/css/style.css**
- Variáveis --azul-escuro e --vermelho-acento definidas
- Classes obrigatórias presentes: .banner-demo, .navbar-custom, .kpi-card, .kpi-valor, .kpi-label, .kpi-icon, .card-header-custom, .thead-custom, .footer-custom
- @media (max-width: 576px) presente para responsividade mobile

**static/js/main.js**
- Todas as 4 funções de fetch existem e são chamadas no DOMContentLoaded
- Cada função busca do endpoint correto (sem URLs hardcoded com host/porta)
- formatarReais() usa toLocaleString('pt-BR', ...)
- Charts inicializados no canvas correto (ids batem com o HTML)
- .catch(err => ...) em todos os fetch
- Sem console.log de depuração (apenas .catch)
- Sem imports de npm/node/webpack — JS puro com fetch

**requirements.txt**
- Flask==3.0.3 presente com versão fixada
- gunicorn==22.0.0 presente com versão fixada
- Sem dependências desnecessárias

**Procfile**
- Conteúdo exato: web: gunicorn app:app

Aponte apenas problemas reais. Não sugira refatorações além do que foi especificado.
Não modifique nenhum arquivo — apenas reporte o que precisa de correção com o nome do arquivo e a linha ou seção onde o problema está.
```
