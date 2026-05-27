# Padrao de dashboard Base Exata

Este documento define a estrutura recomendada para dashboards em apps Flask da Base Exata, usando o `estoque-app` como base.

## Objetivo do dashboard

Um dashboard da Base Exata deve responder, em poucos segundos:

- O que esta acontecendo agora?
- Quais indicadores merecem atencao?
- Onde existe risco operacional ou oportunidade?
- Qual deve ser a proxima acao do usuario?

## Estrutura de pagina

Ordem recomendada:

1. Layout base com sidebar e topbar.
2. Linha de KPIs principais.
3. Bloco de graficos principais.
4. Bloco de alertas, rankings ou excecoes.
5. Tabela operacional com registros recentes ou itens criticos.
6. Estados vazios e mensagens de demo quando aplicavel.

## Template estrutural

```html
{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block page_title %}Dashboard{% endblock %}

{% block content %}
<div class="row g-3 mb-4">
  <!-- KPIs -->
</div>

<div class="row g-3 mb-4">
  <div class="col-lg-8">
    <!-- Grafico principal -->
  </div>
  <div class="col-lg-4">
    <!-- Grafico complementar -->
  </div>
</div>

<div class="row g-3">
  <div class="col-lg-5">
    <!-- Alertas / ranking / excecoes -->
  </div>
  <div class="col-lg-7">
    <!-- Tabela operacional -->
  </div>
</div>
{% endblock %}
```

## KPIs

Quantidade recomendada:

- 3 a 4 KPIs no topo.
- No desktop, cada KPI usa `col-lg-3`.
- No mobile/tablet, usar `col-6` para manter leitura compacta.

Tipos comuns:

- Total operacional: produtos ativos, clientes ativos, pedidos, processos.
- Valor financeiro: estoque, faturamento, custo, economia estimada.
- Alerta: abaixo do minimo, pendencias, atrasos, inconsistencias.
- Atividade recente: movimentacoes hoje, registros processados, importacoes.

Regra de cor:

- `--teal`: atividade ou status positivo/neutro.
- `--navy`: metrica principal ou financeira.
- `--brick`: alerta ou excecao.

## Graficos principais

Composicao recomendada:

- Grafico dominante a esquerda (`col-lg-8`) com evolucao temporal, comparativo ou volume.
- Grafico complementar a direita (`col-lg-4`) com distribuicao por categoria, status ou origem.

Padroes:

- Barras para comparacao por periodo.
- Donut para composicao por categoria.
- Barras horizontais para rankings.
- Evitar graficos de pizza com muitas categorias; se houver muitas, agrupar como `Outros`.

Alturas:

- Dashboard principal: `250px`.
- Ranking horizontal ou relatorio mais denso: `320px`.

## Alertas e excecoes

Use um container lateral para aquilo que precisa de acao.

Exemplos:

- Estoque abaixo do minimo.
- Produtos sem movimentacao.
- Pedidos atrasados.
- Clientes sem retorno.
- Registros com erro de importacao.

Padrao visual:

- Container `chart-container`.
- Titulo com icone de alerta quando fizer sentido.
- Lista curta com ate 5 itens.
- Badge semantico no final da linha.
- Barra de progresso fina quando houver proporcao ou meta.
- Link `Ver todos` com `btn btn-sm btn-outline-secondary`.

## Tabela operacional

A tabela deve trazer detalhe acionavel, nao repetir todos os dados do sistema.

Exemplos:

- Ultimas movimentacoes.
- Ultimos pedidos.
- Maiores divergencias.
- Top itens por impacto.
- Registros pendentes de revisao.

Regras:

- Usar `table-container`.
- Cabecalhos curtos.
- Nomes principais em `fw-semibold`.
- Metadados em `small` ou `text-muted`.
- Badges para tipo/status.
- Datas em formato local.
- Valores monetarios alinhados a direita.

## Filtros

Filtros devem aparecer abaixo do titulo ou dentro de um `chart-container` acima da tabela/lista.

Padrao recomendado:

- Usar grid Bootstrap.
- Botao principal `btn-navy`.
- Botao de limpar `btn-outline-secondary`.
- Labels curtos e consistentes.
- Evitar filtros na topbar quando passarem de um ou dois controles.

## Estados vazios

Todo bloco dinamico precisa de estado vazio.

Padrao:

- Manter o container visivel.
- Usar icone simples.
- Texto curto: `Nenhuma movimentacao nos ultimos 30 dias.` ou `Todos os produtos estao acima do minimo.`
- Evitar texto tecnico.

## Mensagem de demo

Como os apps sao vitrines comerciais, dashboards devem deixar claro quando os dados sao simulados.

Locais possiveis:

- Sidebar footer: `Demo`.
- Topbar: badge `Dados simulados`.
- Primeiro bloco do dashboard: alerta informativo discreto.

Texto base:

```text
Dados demonstrativos para apresentacao. Valores e movimentacoes sao ficticios.
```

## Responsividade

Desktop:

- Sidebar fixa com `260px`.
- Conteudo com margem esquerda.
- KPIs em 4 colunas.
- Graficos em `8/4`.
- Alertas e tabela em `5/7`.

Mobile:

- Sidebar recolhida com botao na topbar.
- Backdrop escuro ao abrir menu.
- Conteudo ocupa 100% da largura.
- KPIs em 2 colunas.
- Graficos e tabelas empilham.
- Tabelas sempre dentro de `table-responsive`.

## Checklist antes de criar novo dashboard

- O dashboard tem 3 ou 4 KPIs realmente importantes?
- A primeira linha mostra a situacao atual sem precisar rolar a tela?
- Existe pelo menos um bloco que aponta risco, excecao ou proxima acao?
- Graficos usam as cores semanticas da Base Exata?
- Tabelas estao responsivas e com cabecalhos curtos?
- Estados vazios foram definidos?
- Dados simulados estao identificados quando for demo?
- A tela funciona sem alterar o padrao global de sidebar/topbar?

## Checklist de consistencia visual

- Usar `Inter`.
- Usar fundo geral `#f0f2f5`.
- Usar containers brancos com raio `12px` e borda `#e8ecf0`.
- Usar `--navy` para titulos e valores principais.
- Usar `--teal` para entrada/positivo/neutro.
- Usar `--brick` para saida/alerta/destaque.
- Usar Bootstrap Icons alinhados ao tema da secao.
- Evitar novas cores sem necessidade.
