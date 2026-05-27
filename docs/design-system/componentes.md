# Componentes visuais Base Exata

Referencia pratica para reutilizar componentes visuais dos apps Flask da Base Exata. Os exemplos abaixo descrevem o padrao atual do `estoque-app`; nao sao uma biblioteca pronta.

## Tokens CSS recomendados

```css
:root {
  --navy: #1A365D;
  --navy-light: #234782;
  --brick: #D35400;
  --brick-light: #E8731A;
  --teal: #008080;
  --snow: #F8F9FA;
  --graphite: #2C3E50;
  --sidebar-w: 260px;
}
```

## Layout base

Estrutura padrao:

```html
<aside class="sidebar">...</aside>
<div class="main-content">
  <div class="top-bar">...</div>
  <div class="page-content">
    ...
  </div>
</div>
```

Regras:

- `main-content` deve ter `margin-left: var(--sidebar-w)` no desktop.
- `page-content` usa padding `1.5rem`.
- No mobile, a sidebar fica oculta e `main-content` volta para `margin-left: 0`.
- Backdrop mobile deve ficar abaixo da sidebar e acima do conteudo.

## Sidebar

Elementos:

- `sidebar-brand`: marca e subtitulo do app.
- `sidebar-nav`: links agrupados.
- `nav-section`: rotulos de grupos em uppercase.
- `sidebar-footer`: assinatura da Base Exata e indicacao de demo.

Padrao de link:

```html
<a href="#" class="active">
  <i class="bi bi-grid-1x2-fill"></i> Dashboard
</a>
```

Uso:

- Um link ativo por vez.
- Icones devem ter largura fixa para alinhar labels.
- Badges de contagem podem ser usados no final do link, como alertas pendentes.

## Topbar

Padrao:

```html
<div class="top-bar">
  <div class="d-flex align-items-center gap-3">
    <button class="btn btn-sm btn-light d-lg-none">...</button>
    <h6 class="mb-0 fw-bold" style="color:var(--navy)">Dashboard</h6>
  </div>
  <div class="d-flex align-items-center gap-2">
    <span class="badge bg-light text-dark">{{ data_atual }}</span>
  </div>
</div>
```

Uso:

- Titulo curto da pagina.
- Badges pequenos de data, ambiente ou demo.
- Nao colocar navegacao secundaria extensa na topbar.

## Section header

Usar quando a pagina precisar de titulo interno e acao de topo.

```html
<div class="section-header">
  <h4><i class="bi bi-box-seam-fill me-2" style="color:var(--teal)"></i>Produtos</h4>
  <a class="btn btn-navy btn-sm" href="#">Novo produto</a>
</div>
```

Regras:

- Titulo em `h4`, peso `700`, cor `--navy`.
- Icone em `--teal` quando o titulo for informativo.
- Acoes de criacao usam `btn-navy`.

## KPI card

Padrao:

```html
<div class="stat-card">
  <div class="d-flex align-items-center gap-3">
    <div class="stat-icon" style="background:rgba(0,128,128,0.1); color:var(--teal)">
      <i class="bi bi-box-seam-fill"></i>
    </div>
    <div>
      <div class="stat-value">128</div>
      <div class="stat-label">Produtos Ativos</div>
    </div>
  </div>
</div>
```

Variacoes:

- `--teal`: quantidade, entrada, atividade ou status saudavel.
- `--navy`: valor financeiro, total institucional ou metrica principal.
- `--brick`: alerta, excecao, saida ou risco.

Boas praticas:

- Label deve explicar a unidade do valor.
- Evitar mais de 4 KPIs no topo.
- Para valores monetarios longos, reduzir o tamanho do valor para `1.3rem`.

## Chart container

Padrao:

```html
<div class="chart-container">
  <div class="d-flex align-items-center justify-content-between mb-3">
    <h6 class="mb-0">Movimentacoes - Ultimos 7 Dias</h6>
    <span class="badge bg-light text-muted">Atualizado agora</span>
  </div>
  <div style="position:relative; height:250px;">
    <canvas id="chartMov7d"></canvas>
  </div>
</div>
```

Regras:

- Sempre definir altura do canvas.
- Titulos de grafico devem ser descritivos e curtos.
- Quando houver atualizacao ou periodo, usar badge neutro.
- Usar cores semanticas consistentes entre paginas.

## Table container

Padrao:

```html
<div class="table-container">
  <div class="table-responsive">
    <table class="table table-hover">
      <thead>
        <tr>
          <th>Produto</th>
          <th>Tipo</th>
          <th class="text-end">Valor</th>
        </tr>
      </thead>
      <tbody>...</tbody>
    </table>
  </div>
</div>
```

Regras:

- Numeros financeiros e totais ficam alinhados a direita.
- Contagens e quantidades podem ficar centralizadas.
- Nome principal usa `fw-semibold`.
- Metadados usam `small` ou `text-muted`.
- Use `table-sm` para relatorios densos, `table-hover` para listas navegaveis.

## Badges

Classes semanticas:

```css
.badge-entrada { background: #d4edda; color: #155724; }
.badge-saida { background: #f8d7da; color: #721c24; }
.badge-alerta { background: #fff3cd; color: #856404; }
.badge-critico { background: #f8d7da; color: #721c24; }
```

Uso recomendado:

- `badge-entrada`: entrada, adicao, balanco positivo.
- `badge-saida`: saida, retirada, balanco negativo.
- `badge-alerta`: atencao, estoque baixo, item sem movimentacao.
- `badge-critico`: estoque zero, falha, risco alto.
- `bg-light text-dark`: categoria, margem, data e informacao neutra.

## Botoes

Classes:

```css
.btn-navy { background: var(--navy); color: #fff; border: none; }
.btn-brick { background: var(--brick); color: #fff; border: none; }
.btn-teal { background: var(--teal); color: #fff; border: none; }
```

Uso:

- `btn-navy`: acao primaria, salvar, criar, aplicar filtro.
- `btn-brick`: acao de destaque comercial ou alerta controlado.
- `btn-teal`: acao positiva ou operacional secundaria.
- `btn-outline-secondary`: navegar para detalhe, ver todos, limpar filtro.
- `btn-outline-danger`: remover/excluir, sempre com confirmacao quando destrutivo.

## Formularios

Padrao visual observado:

- Labels com peso `600`, tamanho `0.85rem`, cor `--navy`.
- Foco em inputs e selects com borda `--teal` e sombra `rgba(0,128,128,0.15)`.
- Formularios devem ficar dentro de `chart-container` quando forem paginas simples.
- Botao principal deve ficar no fim do formulario, usando `btn-navy`.

## Alertas e mensagens

Mensagens flash usam o componente `alert` do Bootstrap com fonte reduzida.

Regras:

- Mensagens de sucesso devem confirmar a acao executada.
- Mensagens de erro devem indicar a correcao esperada.
- Mensagens de demo devem ser discretas e visiveis.

Texto recomendado para demos:

```text
Dados demonstrativos para apresentacao. Valores e movimentacoes sao ficticios.
```

## Estados vazios

Padrao:

```html
<div class="text-center py-4">
  <i class="bi bi-check-circle-fill text-success fs-2"></i>
  <p class="text-muted mt-2 mb-0" style="font-size:0.875rem">Nenhum alerta encontrado.</p>
</div>
```

Regras:

- Usar icone simples.
- Texto curto e direto.
- Nao esconder o container; manter a area para preservar a estrutura visual.

## Graficos Chart.js

Configuracao visual recomendada:

- `responsive: true`.
- `maintainAspectRatio: false`.
- Legenda no rodape.
- Labels de legenda com fonte entre `10` e `11`.
- Barras com `borderRadius` entre `4` e `6`.
- Grid horizontal em `#f0f2f5`.
- Grid vertical desligado quando nao agregar leitura.

Paleta para graficos categoricos:

```js
const cores = ['#1A365D', '#D35400', '#008080', '#2C3E50', '#E8731A', '#234782', '#00A3A3', '#5D7083'];
```
