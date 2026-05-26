# Base Exata

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-blue)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-web%20apps-000000?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-demo%20data-003B57?logo=sqlite&logoColor=white)
![Deploy](https://img.shields.io/badge/deploy-Render-46E3B7?logo=render&logoColor=black)

**Base Exata** é um projeto de consultoria em **análise de dados, automação, dashboards e sistemas internos simples** para comércios, supermercados, pequenas indústrias e negócios locais da região de **Capivari, SP**.

A proposta é transformar informações desorganizadas, controles manuais e processos repetitivos em soluções práticas para o dia a dia da empresa: painéis de indicadores, sistemas de apoio à operação, relatórios automatizados e páginas profissionais para captação de clientes.

---

## Visão geral

A Base Exata une duas frentes principais:

1. **Presença digital e captação**  
   Landing page institucional, contato via formulário/WhatsApp, apresentação dos serviços e portfólio de soluções.

2. **Portfólio técnico demonstrável**  
   Conjunto de micro-aplicações web em Flask, com dados simulados, criadas para demonstrar problemas reais que a consultoria pode resolver em empresas locais.

O repositório funciona como uma vitrine prática: em vez de apenas descrever os serviços, ele apresenta aplicações executáveis que simulam cenários de vendas, estoque, produção, relatórios, sazonalidade e performance comercial.

---

## Problemas que o projeto busca resolver

A Base Exata foi pensada para negócios que enfrentam desafios como:

- controles em papel, caderno ou planilhas soltas;
- falta de indicadores confiáveis para tomada de decisão;
- dificuldade para acompanhar vendas, estoque, produção ou equipe comercial;
- retrabalho com relatórios manuais;
- ausência de site ou presença digital profissional;
- baixa clareza sobre quais dados realmente importam para a gestão;
- dependência de processos informais que não escalam.

A ideia central é entregar soluções simples, visuais e acessíveis, com foco no uso real pelo gestor e pela equipe.

---

## Estrutura atual do repositório

```text
Base-Exata/
├── README.md
├── landing-page/
│   ├── index.html
│   └── sucesso.html
├── estoque-app/
│   ├── app.py
│   ├── seed_data.py
│   ├── requirements.txt
│   ├── Procfile
│   ├── templates/
│   └── static/
└── portifolio/
    ├── COMO_RODAR.md
    ├── CLAUDE.md
    ├── SESSOES.md
    ├── projeto-1-vendas/
    ├── projeto-2-estoque/
    ├── projeto-3-oee/
    ├── projeto-4-relatorios/
    ├── projeto-5-sazonalidade/
    └── projeto-6-performance/
```

> Observação: a pasta está nomeada como `portifolio/` no repositório. Mantive esse nome aqui para refletir a estrutura real do projeto.

---

## Landing page

A pasta `landing-page/` contém a página institucional da Base Exata.

Principais recursos:

- HTML estático em português;
- layout responsivo;
- identidade visual própria;
- SEO básico com `title`, `description`, `keywords`, canonical e Open Graph;
- Schema.org do tipo `LocalBusiness`;
- Google Analytics 4;
- Tailwind CSS via CDN;
- Alpine.js para interações;
- formulário de contato com FormSubmit;
- botão flutuante de WhatsApp;
- seção de serviços;
- seção de portfólio com links para demos hospedadas no Render.

### Tecnologias usadas na landing page

- HTML5
- Tailwind CSS via CDN
- Alpine.js
- Google Analytics 4
- Schema.org
- FormSubmit

---

## Aplicações e demos

### 1. Dashboard de Inteligência de Vendas

**Pasta:** `portifolio/projeto-1-vendas/`  
**Objetivo:** demonstrar um painel de vendas para acompanhamento de faturamento, ticket médio, evolução semanal e ranking de produtos.

**Principais pontos técnicos:**

- Flask;
- SQLite;
- APIs JSON para alimentar gráficos;
- Chart.js;
- dados simulados de vendas.

---

### 2. Sistema de Gestão de Estoque

**Pastas:**

- `estoque-app/`
- `portifolio/projeto-2-estoque/`

**Objetivo:** simular um sistema simples para controle de produtos, movimentações, entradas, saídas e alertas de estoque mínimo.

**Principais pontos técnicos:**

- Flask;
- SQLite;
- cadastro de produtos;
- movimentações de estoque;
- indicadores operacionais;
- dados populados automaticamente por seed.

---

### 3. Monitor de Eficiência Industrial OEE

**Pasta:** `portifolio/projeto-3-oee/`  
**Objetivo:** demonstrar um painel industrial para acompanhamento de eficiência produtiva usando OEE.

O projeto trabalha com indicadores de:

- disponibilidade;
- performance;
- qualidade;
- OEE geral;
- OEE por máquina;
- histórico diário;
- mapa de calor por máquina e turno.

---

### 4. Automação de Relatórios Gerenciais

**Pasta:** `portifolio/projeto-4-relatorios/`  
**Objetivo:** simular a consolidação automática de relatórios gerenciais, reduzindo o tempo gasto com planilhas manuais.

O projeto contempla análises de:

- faturamento;
- categorias;
- fornecedores;
- ticket médio;
- rankings gerenciais.

---

### 5. Análise de Sazonalidade e Demanda

**Pasta:** `portifolio/projeto-5-sazonalidade/`  
**Objetivo:** demonstrar análise de tendência e previsão de demanda para apoiar compras, estoque e planejamento comercial.

O projeto utiliza dados simulados para analisar:

- vendas diárias;
- produtos;
- categorias;
- previsões mensais;
- comportamento sazonal.

---

### 6. Painel de Performance Comercial

**Pasta:** `portifolio/projeto-6-performance/`  
**Objetivo:** apresentar um painel de gestão comercial para acompanhamento de vendedores, regiões, metas e faturamento.

O projeto contempla:

- ranking de vendedores;
- comparação entre meta e realizado;
- faturamento por região;
- status de vendas;
- indicadores de performance comercial.

---

## Portfólio publicado na landing page

A landing page referencia as seguintes demos:

| Projeto | Link |
|---|---|
| Dashboard de Inteligência de Vendas | [baseexata-vendas.onrender.com](https://baseexata-vendas.onrender.com) |
| Sistema de Gestão de Estoque | [estoque-app-nzd4.onrender.com](https://estoque-app-nzd4.onrender.com) |
| Monitor de Eficiência Industrial OEE | [baseexata-oee.onrender.com](https://baseexata-oee.onrender.com) |
| Automação de Relatórios Gerenciais | [baseexata-relatorios.onrender.com](https://baseexata-relatorios.onrender.com) |
| Análise de Sazonalidade e Demanda | [baseexata-sazonalidade.onrender.com](https://baseexata-sazonalidade.onrender.com) |
| Painel de Performance Comercial | [baseexata-performance.onrender.com](https://baseexata-performance.onrender.com) |

---

## Stack técnica

### Desenvolvimento web

- HTML5
- CSS3
- Tailwind CSS
- Bootstrap 5
- Alpine.js
- JavaScript

### Backend e dados

- Python
- Flask
- SQLite
- APIs JSON
- Scripts de seed para dados demonstrativos

### Visualização e BI

- Chart.js
- Indicadores operacionais
- Dashboards simulados
- Modelagem simples de dados

### Deploy e operação

- Render
- Gunicorn
- Procfile
- FormSubmit
- Google Analytics

---

## Como rodar localmente

### Rodar uma aplicação Flask do portfólio

Escolha um projeto dentro de `portifolio/` e execute:

```bash
cd portifolio/projeto-1-vendas
pip install -r requirements.txt
python app.py
```

Depois acesse:

```text
http://localhost:5000
```

Para rodar outro projeto, entre na pasta correspondente:

```bash
cd portifolio/projeto-2-estoque
cd portifolio/projeto-3-oee
cd portifolio/projeto-4-relatorios
cd portifolio/projeto-5-sazonalidade
cd portifolio/projeto-6-performance
```

Cada aplicação é independente e possui seu próprio banco SQLite.

---

### Rodar o app de estoque standalone

```bash
cd estoque-app
pip install -r requirements.txt
python app.py
```

Acesse:

```text
http://localhost:5000
```

---

### Abrir a landing page localmente

Como a landing page é estática, é possível abrir diretamente o arquivo:

```text
landing-page/index.html
```

Ou servir a pasta localmente com Python:

```bash
cd landing-page
python -m http.server 8000
```

Acesse:

```text
http://localhost:8000
```

---

## Padrão das micro-aplicações Flask

As aplicações do portfólio seguem uma estrutura semelhante:

```text
projeto-x/
├── app.py
├── seed_data.py
├── requirements.txt
├── Procfile
├── templates/
│   ├── base.html
│   └── index.html
├── static/
│   ├── css/
│   └── js/
└── database.db
```

O arquivo `database.db` é gerado automaticamente em ambiente local/produção e não deve ser tratado como fonte principal do projeto.

---

## Dados utilizados

Os dados das aplicações são **simulados** e servem apenas para demonstração técnica e comercial.

Este repositório não deve armazenar:

- dados reais de clientes;
- bases reais de empresas prospectadas;
- telefones coletados em massa;
- informações comerciais privadas;
- dados internos de empresas atendidas;
- credenciais, tokens ou chaves de API.

As bases reais de prospecção e atendimento devem ficar em ambientes privados e controlados, como Google Sheets privado, CRM, banco de dados interno ou repositórios privados.

---

## Posicionamento comercial

A Base Exata pode ser apresentada para negócios locais como uma consultoria prática para:

- criar dashboards de vendas, estoque, produção ou atendimento;
- automatizar relatórios recorrentes;
- organizar bases de dados e planilhas;
- construir sistemas internos simples;
- criar landing pages e páginas de apresentação;
- estruturar indicadores para tomada de decisão;
- transformar controles manuais em processos mais confiáveis.

A comunicação do projeto prioriza clareza, linguagem simples e foco na dor real do negócio, antes da escolha da ferramenta.

---

## Status atual

- [x] Landing page institucional criada
- [x] Formulário de contato configurado
- [x] Botão de WhatsApp na landing page
- [x] SEO básico e Schema.org adicionados
- [x] Portfólio com 6 micro-aplicações definido
- [x] Apps Flask com SQLite e dados simulados
- [x] Demos referenciadas na landing page
- [ ] Adicionar screenshots das aplicações no README
- [ ] Criar documentação comercial dos serviços
- [ ] Criar modelo de proposta comercial
- [ ] Criar dashboard interno de prospecção
- [ ] Evoluir processo de captação com Apify + Google Sheets
- [ ] Documentar estudos de caso reais de forma anonimizada

---

## Próximos passos sugeridos

1. Adicionar imagens ou GIFs das demos no README.
2. Criar uma pasta `docs/` com materiais comerciais, proposta, diagnóstico e roteiro de atendimento.
3. Separar dados reais de prospecção em ambiente privado.
4. Criar um painel interno para acompanhar leads, status de contato e conversão.
5. Padronizar nomes de pastas e deploys conforme o projeto crescer.
6. Criar issues no GitHub para organizar melhorias técnicas e comerciais.

---

## Autor

Desenvolvido por **Gabriel Lopes Cavallari**.

Atuação voltada a **Business Intelligence, análise de dados, automação de processos, sistemas internos e soluções digitais para negócios locais**.

- GitHub: [@GabrielCavallari](https://github.com/GabrielCavallari)
- LinkedIn: [Gabriel Lopes Cavallari](https://www.linkedin.com/in/gabriel-lopes-cavallari-18106020a/)

---

## Licença

Este projeto está em desenvolvimento. A licença poderá ser definida conforme a evolução da Base Exata.
