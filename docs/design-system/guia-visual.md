# Guia visual Base Exata para apps Flask

Este guia documenta o padrao visual usado no `estoque-app` e deve ser usado como referencia para novos apps Flask da Base Exata. O objetivo e manter demos com aparencia consistente, clara e comercialmente apresentavel, sem transformar cada app em um produto visual diferente.

## Principios visuais

- Clareza operacional antes de decoracao: telas devem mostrar rapidamente situacao, alertas e proximas acoes.
- Aparencia consultiva: usar visual limpo, dados bem organizados e linguagem objetiva.
- Demos explicitas: quando os dados forem simulados, a interface deve deixar isso claro.
- Hierarquia previsivel: sidebar para navegacao, topbar para contexto, conteudo em cards, graficos e tabelas.

## Paleta de cores

Paleta principal extraida do `estoque-app/templates/base.html`.

| Token | Hex | Uso recomendado |
| --- | --- | --- |
| `--navy` | `#1A365D` | Cor institucional principal, sidebar, titulos, valores de KPI e botoes primarios |
| `--navy-light` | `#234782` | Hover de botao primario e variacoes do navy |
| `--brick` | `#D35400` | Destaque comercial, alertas de atencao, saidas, estado ativo na sidebar |
| `--brick-light` | `#E8731A` | Hover de botao brick e variacoes de destaque |
| `--teal` | `#008080` | Indicadores positivos/neutros, entradas, icones de secao e graficos |
| `--snow` | `#F8F9FA` | Fundos leves de cabecalho de tabela e areas sutis |
| `--graphite` | `#2C3E50` | Texto principal |
| Fundo da pagina | `#f0f2f5` | Fundo geral do app |
| Borda leve | `#e8ecf0` | Bordas de cards, tabelas, topbar e containers |
| Texto secundario | `#8898aa` | Labels, metadados e textos auxiliares |

Escala semantica usada em operacoes:

- Entrada: fundo `#d4edda`, texto `#155724`.
- Saida/critico: fundo `#f8d7da`, texto `#721c24`.
- Alerta: fundo `#fff3cd`, texto `#856404`.
- Sucesso visual: usar verde Bootstrap apenas em mensagens de confirmacao ou estado resolvido.

## Tipografia

- Fonte padrao: `Inter`, carregada pelo Google Fonts.
- Pesos usados: `300`, `400`, `500`, `600`, `700`.
- Corpo: `0.875rem` para tabelas e conteudo denso.
- Labels auxiliares: `0.75rem` a `0.8rem`, com cor secundaria.
- Titulos de pagina/secao: peso `700`, cor `--navy`.
- Titulos de cards/graficos: `0.85rem`, peso `600`, cor `--navy`.
- Valores de KPI: `1.6rem`, peso `700`, cor `--navy`; reduzir para `1.3rem` quando o valor for monetario longo.

## Padrao de sidebar

A sidebar e fixa no desktop e recolhivel no mobile.

- Largura padrao: `260px`.
- Fundo: `--navy`.
- Marca no topo com nome `Base Exata` e subtitulo do app em caixa alta.
- Separar links por secoes curtas, como `Principal`, `Operacoes` e `Analise`.
- Links com icone Bootstrap Icons, label simples e peso `500`.
- Estado normal: texto branco com opacidade aproximada de `60%`.
- Hover: texto branco e fundo branco com opacidade baixa.
- Estado ativo: texto branco, fundo branco com opacidade baixa e borda esquerda `--brick`.
- Footer: texto pequeno com `Base Exata Consultoria`, cidade e indicacao de demo quando aplicavel.
- Mobile: esconder com `transform: translateX(-100%)`, exibir via classe `show` e usar backdrop escuro.

## Padrao de topbar

A topbar deve dar contexto, nao competir com o conteudo.

- Fundo branco, borda inferior `#e8ecf0`.
- Posicao sticky no topo.
- Altura visual compacta com padding `0.75rem 1.5rem`.
- Esquerda: botao de menu no mobile e titulo da pagina.
- Direita: badges leves de contexto, como data atual, ambiente ou status da demo.
- Evitar filtros complexos na topbar; filtros devem ficar em containers proprios dentro da pagina.

## Cards de KPI

Cards de KPI sao usados no topo dos dashboards para leitura rapida.

- Fundo branco, borda `#e8ecf0`, raio `12px`, padding `1.25rem`.
- Layout interno: icone a esquerda, valor e label a direita.
- Icone: caixa de `48px` por `48px`, raio `10px`, fundo em cor principal com opacidade `10%`.
- Usar `--teal` para indicadores positivos/neutros, `--navy` para valores financeiros e `--brick` para alertas.
- Valor com peso `700`; label com `#8898aa`, peso `500`.
- Hover discreto: sombra `0 4px 20px rgba(26,54,93,0.08)`.
- Grid recomendado: 4 cards em desktop, 2 por linha em telas medias/pequenas.

## Containers de graficos

Graficos devem morar em `chart-container`.

- Fundo branco, borda `#e8ecf0`, raio `12px`, padding `1.25rem`.
- Titulo `h6` com `0.85rem`, peso `600`, cor `--navy`.
- Altura explicita para canvas, normalmente `250px` a `320px`.
- Legenda preferencial no rodape.
- Grade discreta em `#f0f2f5`.
- Barras de entrada usam `rgba(0,128,128,0.7)`.
- Barras de saida usam `rgba(211,84,0,0.7)`.
- Graficos donut usam a sequencia: `#1A365D`, `#D35400`, `#008080`, `#2C3E50`, `#E8731A`, `#234782`, `#00A3A3`, `#5D7083`.

## Tabelas

Tabelas devem ser densas, legiveis e dentro de `table-container`.

- Container branco, borda leve, raio `12px` e `overflow: hidden`.
- Cabecalho com fundo `--snow`, texto uppercase, `0.75rem`, peso `600`, cor `#8898aa`.
- Celulas com padding `0.75rem 1rem`, fonte `0.875rem`, borda inferior `#f0f2f5`.
- Usar `table-responsive` para telas pequenas.
- Usar `fw-semibold` para nomes principais e `text-muted` para metadados.
- Codigos/SKUs podem usar `code` com cor `--navy` e fonte pequena.
- Linhas de atencao podem usar `table-warning`, mas sem excesso.

## Badges

Badges devem comunicar status sem virar elemento decorativo.

- Entrada: classe visual `badge-entrada`, para acrescimos, entradas e balanco positivo.
- Saida: classe visual `badge-saida`, para retiradas e balanco negativo.
- Alerta: classe visual `badge-alerta`, para estoque baixo, pendencia ou risco moderado.
- Critico: classe visual `badge-critico`, para ruptura, estoque zero ou falha relevante.
- Neutro: `bg-light text-dark`, para categorias, datas, margens e metadados.
- Tamanho pequeno em navegacao: cerca de `0.65rem`.
- Tamanho padrao em conteudo: manter o padrao Bootstrap.

## Botoes

Os botoes seguem Bootstrap com classes semanticas do app.

- Primario institucional: `btn-navy`, fundo `--navy`, hover `--navy-light`.
- Destaque/acao comercial: `btn-brick`, fundo `--brick`, hover `--brick-light`.
- Acao positiva/neutra: `btn-teal`, fundo `--teal`, hover `#009999`.
- Acoes secundarias: `btn-outline-secondary` ou `btn-light`.
- Botoes pequenos em headers de cards devem usar `btn-sm` e fonte proxima de `0.75rem`.
- Evitar muitos botoes coloridos na mesma area; uma tela deve ter uma acao primaria clara.

## Mensagens de demo

Como os apps sao vitrines comerciais com dados simulados, a interface deve informar isso de forma simples.

Padroes recomendados:

- Sidebar footer: `Base Exata Consultoria`, localidade e `Demo`.
- Topbar: badge leve com `Demo`, `Dados simulados` ou data de referencia.
- Tela inicial ou dashboard: alerta informativo discreto quando necessario: `Dados demonstrativos para apresentacao. Valores e movimentacoes sao ficticios.`
- Readme e materiais comerciais devem repetir que a demo nao usa dados reais do cliente.

Evitar:

- Chamar dados simulados de "dados reais".
- Prometer resultados garantidos.
- Usar avisos grandes demais que atrapalhem a leitura da demo.

## Estrutura recomendada para dashboards

Ordem visual recomendada:

1. Sidebar fixa com navegacao principal.
2. Topbar com titulo da pagina e contexto.
3. Linha de KPIs principais.
4. Linha de graficos principais, com grafico dominante a esquerda e complemento a direita.
5. Linha de alertas, rankings ou listas operacionais.
6. Tabela de detalhe ou ultimos registros.
7. Estados vazios claros, com icone e texto curto.

Grid recomendado:

- `row g-3 mb-4` para blocos principais.
- KPIs: `col-6 col-lg-3`.
- Grafico principal: `col-lg-8`.
- Grafico complementar: `col-lg-4`.
- Blocos inferiores: combinacoes `col-lg-5` e `col-lg-7`, ou `col-12` para tabelas amplas.

Cada dashboard deve responder rapidamente:

- Qual e a situacao atual?
- Onde existe alerta?
- Qual indicador mudou recentemente?
- Qual acao o usuario deve tomar depois?
