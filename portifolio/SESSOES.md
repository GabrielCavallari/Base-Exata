# SESSOES.md — Portfólio Base Exata
# Gerado em: 2026-04-08
# Objetivo: implementar projeto-3-oee (Monitor de Eficiência Industrial OEE)

---

## Estado atual

| Módulo | Status | O que falta |
|--------|--------|-------------|
| `projeto-1-vendas` | Completo | — |
| `estoque-app` | Completo (referência oficial) | — |
| `projeto-3-oee` | Pendente | Pasta não existe, todos os arquivos faltam |
| `projeto-4-relatorios` | Pendente | — |
| `projeto-5-sazonalidade` | Pendente | — |
| `projeto-6-performance` | Pendente | — |

---

## Sessões geradas

| # | Agente | Objetivo | Dependência |
|---|--------|----------|-------------|
| A | backend-architect | Backend Flask + SQLite + seed para projeto-3-oee | independente |
| B | frontend-developer | Templates HTML/CSS/JS dark theme para projeto-3-oee | aguardar Sessão A |
| C | code-reviewer | Revisar projeto-3-oee completo | aguardar Sessões A e B |

Sessão B depende da Sessão A: o frontend-developer precisa ler o app.py pronto
para conhecer as rotas exatas antes de criar qualquer arquivo.

---

## Sessão A — backend-architect (independente)

Você é o backend-architect. Crie todos os arquivos do backend do projeto-3-oee
dentro de C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-3-oee/

Antes de começar, leia os dois arquivos abaixo para entender o padrão do portfólio:
- C:/Users/Gabriel/Documents/Base Exata/estoque-app/app.py
- C:/Users/Gabriel/Documents/Base Exata/estoque-app/seed.py

Replique exatamente o mesmo padrão estrutural desses arquivos. Não invente variações.

---

CONTEXTO DO PROJETO

Este é o terceiro projeto de um portfólio de 6 micro-aplicações Flask para a consultoria
Base Exata (Capivari, SP). Cada projeto é totalmente independente: banco próprio, sem
imports entre projetos.

O projeto-3-oee é um Monitor de Eficiência Industrial OEE (Overall Equipment Effectiveness)
com dados simulados de uma pequena indústria do interior de SP.

---

ARQUIVO: app.py

Siga exatamente o padrão do estoque-app/app.py:
- Cabeçalho de comentário: "# Projeto 3 — Monitor de Eficiência Industrial OEE\n# Base Exata | Flask + SQLite"
- Importações: sqlite3, os, datetime/timedelta, Flask/render_template/jsonify
- BASE_DIR = os.path.dirname(os.path.abspath(__file__))
- DATABASE = os.path.join(BASE_DIR, 'database.db')
- Funções: get_db(), criar_tabelas(), banco_vazio(), inicializar_banco()
- Chamada de inicializar_banco() no nível do módulo (após definição, antes das rotas)
- banco_vazio() verifica COUNT(*) na tabela registros_turno
- inicializar_banco() chama criar_tabelas() e, se vazio, importa e chama seed_database(DATABASE) de seed_data.py
- if __name__ == '__main__': app.run(debug=True)

Tabelas a criar em criar_tabelas() via conn.executescript():

  maquinas:
    id INTEGER PRIMARY KEY
    nome TEXT NOT NULL
    setor TEXT NOT NULL
    capacidade_hora INTEGER NOT NULL   -- unidades que a máquina produz por hora em condições ideais

  registros_turno:
    id INTEGER PRIMARY KEY
    maquina_id INTEGER NOT NULL
    data TEXT NOT NULL                  -- formato YYYY-MM-DD
    turno TEXT NOT NULL                 -- valores possíveis: 'A', 'B' ou 'C'
    tempo_planejado_min INTEGER NOT NULL -- tempo programado para o turno em minutos
    tempo_operando_min INTEGER NOT NULL  -- tempo efetivamente em operação em minutos
    producao_total INTEGER NOT NULL      -- unidades produzidas (aprovadas + rejeitadas)
    producao_aprovada INTEGER NOT NULL   -- unidades sem defeito
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id)

Rotas Flask:

  GET /
    Renderiza templates/index.html sem variáveis de contexto.
    Todos os dados vêm via fetch JS nas rotas /api/*.

  GET /api/resumo
    Retorna JSON: {oee_geral, disponibilidade, performance, qualidade}
    Calcular médias gerais de todos os registros.
    Fórmulas (calcular individualmente por registro, depois tirar média):
      disponibilidade = tempo_operando_min / tempo_planejado_min
      performance = (producao_total / capacidade_hora) / (tempo_operando_min / 60)
                    -- produção real por hora dividido pela capacidade ideal por hora
      qualidade = producao_aprovada / producao_total
      oee = disponibilidade * performance * qualidade
    Proteger divisão por zero: se denominador == 0, o componente vale 0.
    Todos os valores retornados como float entre 0 e 1 (não em %).
    Exemplo de retorno: {"oee_geral": 0.7821, "disponibilidade": 0.9103, ...}

  GET /api/oee-por-maquina
    Retorna lista JSON: [{nome, oee, disponibilidade, performance, qualidade}]
    OEE médio de cada máquina considerando todos os seus registros.
    Mesmas fórmulas do /api/resumo calculadas por máquina.
    Ordenar por oee DESC.

  GET /api/oee-historico
    Retorna lista JSON: [{data, oee}]
    OEE médio diário dos últimos 30 dias.
    Para cada dia, calcular o OEE médio de todos os registros daquele dia.
    Se não houver registro num dia, não incluir o dia na lista.
    data no formato DD/MM (string), para uso direto como label de gráfico.
    Ordenar por data ASC (do mais antigo para o mais recente).

  GET /api/heatmap
    Retorna lista JSON: [{maquina, turno_a, turno_b, turno_c}]
    OEE médio por máquina por turno.
    turno_a, turno_b, turno_c são floats entre 0 e 1 (ou null se não houver registro).
    Se não houver registro de uma máquina num turno, retornar null para aquele campo.
    Ordenar por nome de máquina ASC.

---

ARQUIVO: seed_data.py

Função: seed_database(database_path)
  -- recebe o caminho do banco como argumento, igual ao padrão do projeto-2

Máquinas (inserir 8):
  Nome                        | Setor        | capacidade_hora
  "Linha 1 - Envase"          | Produção     | 180
  "Linha 2 - Rotulagem"       | Produção     | 150
  "Linha 3 - Pesagem"         | Produção     | 120
  "Prensa Hidráulica A"       | Conformação  | 90
  "Prensa Hidráulica B"       | Conformação  | 90
  "Extrusora Principal"       | Conformação  | 80
  "Esteira de Embalagem A"    | Embalagem    | 200
  "Compressor Central"        | Utilidades   | 60

Registros de turno:
  Período: últimos 30 dias a partir de hoje (date.today())
  Turnos: A (08h-16h, tempo_planejado_min=480), B (16h-00h, 480), C (00h-08h, 480)
  Nem toda máquina tem registro em todo turno e todo dia — variação realista.
  Gerar aproximadamente 500-550 registros no total.

  Distribuição de OEE por máquina (guia para gerar os valores de seed):
    OEE alto (>= 85%): "Esteira de Embalagem A", "Linha 1 - Envase", "Linha 2 - Rotulagem"
    OEE médio (65-84%): "Linha 3 - Pesagem", "Prensa Hidráulica A", "Extrusora Principal"
    OEE baixo (< 65%): "Prensa Hidráulica B", "Compressor Central"

  Para gerar valores dentro de cada faixa, use variação aleatória nos componentes:
    disponibilidade: float entre 0.75 e 0.99 (máquinas OEE alto) /
                     entre 0.60 e 0.90 (médio) / entre 0.45 e 0.75 (baixo)
    performance: float entre 0.85 e 1.00 / 0.70 e 0.90 / 0.55 e 0.80
    qualidade: float entre 0.97 e 1.00 / 0.92 e 0.98 / 0.85 e 0.95

  Calcular tempo_operando_min = round(disponibilidade * 480)
  Calcular producao_total = round(performance * capacidade_hora * (tempo_operando_min / 60))
  Calcular producao_aprovada = round(qualidade * producao_total)
  Garantir que producao_aprovada <= producao_total sempre.

  Usar import random e from datetime import date, timedelta.
  Conectar com sqlite3.connect(database_path).
  Inserir máquinas primeiro, buscar IDs com SELECT, depois inserir registros.
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

---

## Sessão B — frontend-developer (abrir somente após Sessão A concluída)

Você é o frontend-developer. Crie todos os arquivos de frontend do projeto-3-oee
dentro de C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-3-oee/

OBRIGATÓRIO: leia os seguintes arquivos antes de criar qualquer arquivo:
1. C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-3-oee/app.py
   -- para conhecer as rotas /api/* exatas que o backend expõe
2. C:/Users/Gabriel/Documents/Base Exata/estoque-app/templates/base.html
   -- para entender o padrão de estrutura HTML e estilos inline do portfólio
3. C:/Users/Gabriel/Documents/Base Exata/estoque-app/templates/base.html
   -- para entender o padrão visual consolidado do sistema oficial de estoque
4. C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-1-vendas/static/js/main.js
   -- para entender o padrão de organização do JavaScript

---

CONTEXTO DO PROJETO

Terceiro projeto de um portfólio de 6 micro-aplicações Flask para a consultoria
Base Exata (Capivari, SP). O projeto-3-oee é um Monitor de Eficiência Industrial OEE.

DIFERENCIAL obrigatório deste projeto em relação aos outros: dark theme completo.
Os projetos 1 e 2 usam fundo claro (#f4f6f9). Este projeto usa fundo escuro em
todo o body, cards, tabelas e gráficos.

---

ARQUIVO: templates/base.html

Estrutura idêntica ao estoque-app/templates/base.html, com estas diferenças:

- <html lang="pt-BR"> — sem data-bs-theme (o dark theme é feito via CSS próprio, não Bootstrap)
- Title block padrão: "Monitor OEE | Base Exata"
- CDNs na mesma versão dos outros projetos:
    Bootstrap 5.3.3: https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css
    Bootstrap Icons 1.11.3: https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css
    Chart.js 4.4.4: https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js
    Bootstrap JS 5.3.3: https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js
- Link para static/css/style.css via url_for
- Banner de demonstração obrigatório (div com classe banner-demo, antes da navbar):
    MODO DEMONSTRACAO — Projeto Vitrine | Base Exata
- Navbar com classes "navbar navbar-expand-lg navbar-dark navbar-custom":
    Brand: ícone bi-gear-wide-connected + "Base Exata — Monitor OEE"
    Apenas um link de nav: Dashboard (href="/", ativo sempre)
- main.container.py-4 com {% block content %}
- Footer com classe footer-custom: "Base Exata © 2024 — Análise de Dados e Automação para Varejo e Indústria"
- Script CDN Chart.js antes do main.js
- Script link para static/js/main.js via url_for
- {% block scripts %} após o main.js

---

ARQUIVO: templates/index.html

Herda base.html. Toda a interação é via JavaScript (fetch das rotas /api/*).
Não usar variáveis Jinja2 de contexto — a rota GET / não passa variáveis.

Seção 1 — Narrativa do case (alert estilizado, classe case-destaque):
  Ícone bi-trophy-fill + texto:
  "Case real: Aumentou o OEE médio de 61% para 78% em 90 dias identificando
  paradas não programadas na Prensa Hidráulica B."

Seção 2 — 4 cards KPI em linha (row g-3 mb-4, col-6 col-md-3):
  Card 1: id="kpi-oee"          | ícone bi-speedometer2   | label "OEE Geral"
  Card 2: id="kpi-disponib"     | ícone bi-clock-history  | label "Disponibilidade"
  Card 3: id="kpi-performance"  | ícone bi-lightning-fill | label "Performance"
  Card 4: id="kpi-qualidade"    | ícone bi-check-circle   | label "Qualidade"
  Cada card tem:
    div.kpi-icon (ícone)
    div.kpi-valor com id correspondente ao card (ex: id="valor-oee")
    div.kpi-label com o texto do label
    div.kpi-badge com id correspondente (ex: id="badge-oee") — badge colorido por meta

Seção 3 — Dois gráficos lado a lado (row g-3 mb-4):
  Col esquerda (col-12 col-lg-8): gráfico de barras horizontal "OEE por Máquina"
    canvas id="graficoOeeMaquina"
    Card com card-header-custom e ícone bi-bar-chart-steps
  Col direita (col-12 col-lg-4): gráfico de linha "OEE Diário — 30 dias"
    canvas id="graficoOeeHistorico"
    Card com card-header-custom e ícone bi-graph-up

Seção 4 — Tabela heatmap "OEE por Máquina e Turno" (col-12):
  Card com card-header-custom e ícone bi-grid-3x3
  Tabela responsiva com colunas: Máquina | Turno A | Turno B | Turno C
  Thead com classe thead-custom
  Tbody id="tabelaHeatmap" — preenchido via JavaScript
  Cada célula de turno tem cor de fundo via inline style:
    verde  (#198754) com texto branco se valor >= 0.85
    amarelo (#ffc107) com texto preto se valor >= 0.65 e < 0.85
    vermelho (#dc3545) com texto branco se valor < 0.65
    cinza (#6c757d) com texto branco se valor for null

---

ARQUIVO: static/css/style.css

Dark theme completo. Paleta:
  --fundo-principal: #0d1117
  --fundo-card: #161b22
  --fundo-card-alt: #1c2128
  --borda-card: #30363d
  --texto-principal: #e6edf3
  --texto-muted: #8b949e
  --acento-verde: #3fb950        -- OEE bom (>= 85%)
  --acento-amarelo: #d29922      -- OEE atenção (65-84%)
  --acento-vermelho: #f85149     -- OEE crítico (< 65%)
  --acento-azul: #58a6ff         -- destaques neutros

body:
  background-color: var(--fundo-principal)
  color: var(--texto-principal)
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif
  font-size: 14px

.banner-demo:
  background: #1c2128
  color: var(--acento-azul)
  text-align: center
  padding: 8px 16px
  font-size: 13px
  font-weight: 600
  letter-spacing: 1px
  position: sticky
  top: 0
  z-index: 1050
  border-bottom: 1px solid var(--borda-card)

.navbar-custom:
  background-color: #161b22
  border-bottom: 1px solid var(--borda-card)
  box-shadow: 0 2px 8px rgba(0,0,0,0.4)

.navbar-custom .nav-link:hover,
.navbar-custom .nav-link.active:
  color: var(--acento-azul) !important

.card (override global):
  background-color: var(--fundo-card)
  border: 1px solid var(--borda-card)
  border-radius: 10px

.kpi-card:
  border-radius: 12px
  transition: transform 0.15s ease, box-shadow 0.15s ease

.kpi-card:hover:
  transform: translateY(-2px)
  box-shadow: 0 6px 16px rgba(0,0,0,0.4)

.kpi-icon: font-size: 2rem, margin-bottom: 8px, color: var(--acento-azul)
.kpi-valor: font-size: 1.6rem, font-weight: 700, color: var(--texto-principal), line-height: 1.2
.kpi-label: font-size: 12px, color: var(--texto-muted), margin-top: 4px, text-transform: uppercase, letter-spacing: 0.5px
.kpi-badge: margin-top: 6px

.card-header-custom:
  background-color: var(--fundo-card-alt)
  color: var(--texto-principal)
  border-bottom: 1px solid var(--borda-card)
  border-radius: 10px 10px 0 0 !important

.thead-custom th:
  background-color: var(--fundo-card-alt)
  color: var(--texto-muted)
  font-weight: 500
  font-size: 13px
  text-transform: uppercase
  letter-spacing: 0.4px
  padding: 12px 16px
  border-bottom: 1px solid var(--borda-card)
  border-top: none

table.table (override):
  color: var(--texto-principal)

table.table td, table.table th:
  border-color: var(--borda-card)

.case-destaque:
  background: linear-gradient(135deg, #161b22, #1c2128)
  color: var(--texto-principal)
  border: 1px solid var(--borda-card)
  border-radius: 10px
  padding: 14px 20px

.footer-custom:
  background-color: #161b22
  color: var(--texto-muted)
  font-size: 12px
  border-top: 1px solid var(--borda-card)

Classes de badge OEE (usadas via JavaScript):
  .badge-oee-bom      { background-color: #1a4d2e; color: var(--acento-verde); }
  .badge-oee-atencao  { background-color: #3d2e00; color: var(--acento-amarelo); }
  .badge-oee-critico  { background-color: #3d0f0a; color: var(--acento-vermelho); }

@media (max-width: 576px):
  .kpi-valor: font-size: 1.2rem
  .kpi-icon: font-size: 1.5rem
  .thead-custom th: font-size: 11px, padding: 8px 10px

---

ARQUIVO: static/js/main.js

Organizar em funções nomeadas, uma por responsabilidade. Inicializar tudo no DOMContentLoaded.
Comentários em PT-BR. Sem jQuery, sem frameworks — JS puro.

Função classificarOee(valor):
  -- valor é float entre 0 e 1
  -- retorna 'bom' se valor >= 0.85
  -- retorna 'atencao' se valor >= 0.65 e < 0.85
  -- retorna 'critico' se valor < 0.65

Função formatarPct(valor):
  -- valor é float entre 0 e 1
  -- retorna string com 1 casa decimal e símbolo %
  -- ex: 0.7821 -> "78.2%"

Função corHeatmap(valor):
  -- valor é float entre 0 e 1, ou null
  -- retorna objeto {fundo, texto} com cores hex inline
  -- null: {fundo: '#6c757d', texto: '#fff'}
  -- bom: {fundo: '#198754', texto: '#fff'}
  -- atencao: {fundo: '#ffc107', texto: '#000'}
  -- critico: {fundo: '#dc3545', texto: '#fff'}

Função carregarResumo():
  fetch('/api/resumo')
  Para cada KPI (oee_geral, disponibilidade, performance, qualidade):
    Preencher o elemento com id "valor-{kpi}" com formatarPct(valor)
    Preencher o elemento com id "badge-{kpi}" com badge:
      classe "badge badge-oee-{classificarOee(valor)}"
      texto: "Ótimo" se bom, "Atenção" se atencao, "Crítico" se critico

Função carregarOeeMaquina():
  fetch('/api/oee-por-maquina')
  Renderizar gráfico de barras horizontal no canvas "graficoOeeMaquina"
  Chart.js type: 'bar', indexAxis: 'y'
  Dataset: label "OEE (%)", data em % (valor * 100, arredondado 1 decimal)
  Cor de cada barra determinada pelo classificarOee de cada valor:
    bom -> '#3fb950'
    atencao -> '#d29922'
    critico -> '#f85149'
  backgroundColor: array de cores, uma por máquina
  borderRadius: 4
  Escala X: beginAtZero true, max 100, ticks com sufixo "%"
  Escala X grid: color '#30363d'
  Escala Y grid: color '#30363d'
  Escala X ticks: color '#8b949e'
  Escala Y ticks: color '#e6edf3'
  Plugin legend: display false
  Plugin tooltip: callback para mostrar "OEE: XX.X%"

Função carregarHistorico():
  fetch('/api/oee-historico')
  Renderizar gráfico de linha no canvas "graficoOeeHistorico"
  Chart.js type: 'line'
  Dataset: label "OEE Diário", data em % (valor * 100)
  borderColor: '#58a6ff'
  backgroundColor: 'rgba(88, 166, 255, 0.1)'
  fill: true
  tension: 0.3
  pointRadius: 2
  borderWidth: 2
  Escala Y: beginAtZero false, min: 0, max: 100, ticks com sufixo "%"
  Grid colors: '#30363d'
  Ticks colors: '#8b949e'
  Plugin legend: display false

Função carregarHeatmap():
  fetch('/api/heatmap')
  Para cada item na lista, criar uma <tr> no tbody "tabelaHeatmap":
    <td> com nome da máquina
    <td> para turno_a, turno_b, turno_c:
      Se valor null: exibir "—", usar corHeatmap(null)
      Se valor float: exibir formatarPct(valor), usar corHeatmap(valor)
      Aplicar style="background-color:{fundo}; color:{texto}; text-align:center; font-weight:600;"

document.addEventListener('DOMContentLoaded', function() {
  carregarResumo();
  carregarOeeMaquina();
  carregarHistorico();
  carregarHeatmap();
});

---

CONVENÇÕES OBRIGATÓRIAS

- Comentários em PT-BR
- Nenhuma lib JS além das CDNs já declaradas no base.html (Bootstrap + Chart.js)
- Responsivo de 375px a 1440px
- Fundo escuro em TODOS os elementos: body, cards, tabelas, navbar, footer
- Nenhum fundo branco ou cinza claro em nenhum elemento
- Não criar ou modificar app.py, seed_data.py, requirements.txt ou Procfile
- Não usar npm, node, webpack ou qualquer tooling de frontend

---

## Sessão C — code-reviewer (abrir somente após Sessões A e B concluídas)

Você é o code-reviewer. Revise todos os arquivos criados nas Sessões A e B do projeto-3-oee.

Leia cada arquivo abaixo antes de emitir qualquer avaliação:
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-3-oee/app.py
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-3-oee/seed_data.py
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-3-oee/requirements.txt
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-3-oee/Procfile
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-3-oee/.gitignore
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-3-oee/templates/base.html
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-3-oee/templates/index.html
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-3-oee/static/css/style.css
- C:/Users/Gabriel/Documents/Base Exata/portifólio/projeto-3-oee/static/js/main.js

Verifique especificamente os seguintes pontos. Para cada ponto, informe: OK ou PROBLEMA (com descrição exata do que está errado e em qual linha/trecho).

BACKEND (app.py):

1. Divisão por zero protegida em TODOS os cálculos OEE:
   - tempo_planejado_min == 0 no cálculo de disponibilidade
   - tempo_operando_min == 0 no cálculo de performance (divisão por 60 e por capacidade_hora)
   - producao_total == 0 no cálculo de qualidade
   - capacidade_hora == 0 no cálculo de performance

2. Fórmulas OEE corretas:
   - disponibilidade = tempo_operando_min / tempo_planejado_min (resultado entre 0 e 1)
   - performance = (producao_total / capacidade_hora) / (tempo_operando_min / 60)
     equivalente a: (producao_total * 60) / (capacidade_hora * tempo_operando_min)
   - qualidade = producao_aprovada / producao_total (resultado entre 0 e 1)
   - oee = disponibilidade * performance * qualidade

3. /api/resumo retorna float entre 0 e 1 (não em %, não multiplicado por 100)

4. /api/oee-por-maquina retorna lista ordenada por oee DESC, cada item com:
   nome, oee, disponibilidade, performance, qualidade — todos float entre 0 e 1

5. /api/oee-historico retorna lista com campo "data" no formato DD/MM (não YYYY-MM-DD)
   e campo "oee" float entre 0 e 1, ordenado do mais antigo para o mais recente

6. /api/heatmap retorna null (não 0, não string vazia) para turnos sem registro

7. inicializar_banco() é chamado no nível do módulo (não dentro de uma rota)

8. seed_data.py usa função seed_database(database_path) — não popular_banco, não outro nome

SEED (seed_data.py):

9. Seed insere exatamente 8 máquinas com os setores corretos:
   Produção (3 máquinas), Conformação (3), Embalagem (1), Utilidades (1)

10. producao_aprovada <= producao_total em todos os registros gerados

11. Os valores de OEE resultantes das fórmulas são visualmente distintos entre as 3 faixas:
    - Máquinas OEE alto: resultado final >= 0.80 em média
    - Máquinas OEE baixo: resultado final <= 0.60 em média

FRONTEND (templates + static):

12. Banner "MODO DEMONSTRACAO — Projeto Vitrine | Base Exata" presente no base.html
    antes da navbar (não dentro dela)

13. Dark theme: nenhum fundo branco (#fff) ou cinza claro (#f4f6f9) em nenhum seletor CSS

14. Gráficos Chart.js com cores de grid e ticks adaptadas para fundo escuro
    (não usar cores padrão brancas/pretas do Chart.js)

15. Heatmap: células com valor null exibem "—" e fundo neutro (cinza), não erro JS

16. JavaScript: todas as chamadas fetch apontam para as rotas corretas:
    /api/resumo, /api/oee-por-maquina, /api/oee-historico, /api/heatmap

17. Responsividade: breakpoints col-12/col-lg-* presentes nos gráficos e col-6/col-md-3
    nos cards KPI

18. Comentários e docstrings em PT-BR nos arquivos Python e JS

19. snake_case em todas as variáveis e funções Python

20. database.db presente no .gitignore

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
