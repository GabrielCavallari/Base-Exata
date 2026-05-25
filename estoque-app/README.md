# 📦 Sistema de Gestão de Estoque — Base Exata Consultoria

Sistema web completo para controle de estoque, desenvolvido como projeto-demo da **Base Exata Consultoria** (Capivari, SP).

## Funcionalidades

- **Dashboard** — KPIs em tempo real, gráficos de movimentação e alertas
- **CRUD de Produtos** — Cadastro completo com busca, filtros e ordenação
- **Entrada/Saída** — Registro de movimentações com atualização automática de estoque
- **Alertas** — Produtos abaixo do estoque mínimo, ordenados por urgência
- **Relatórios** — Valor por categoria, movimentação semanal, produtos parados

## Stack

| Componente | Tecnologia |
|---|---|
| Backend | Python 3.11 + Flask |
| Banco de Dados | SQLite |
| Frontend | Bootstrap 5 + Chart.js |
| Deploy | Render (free tier) |

## Executar Localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar (o banco e os dados demo são criados automaticamente)
python app.py
```

Acesse: `http://localhost:5000`

## Deploy no Render

1. Crie um repositório no GitHub e faça push deste projeto
2. No [Render](https://render.com), crie um **New Web Service**
3. Conecte ao repositório
4. O `render.yaml` já configura tudo automaticamente

## Estrutura

```
estoque-app/
├── app.py              # Aplicação Flask (rotas, lógica)
├── seed.py             # Gerador de dados demo (30 produtos + 220 movimentações)
├── wsgi.py             # Entry point para Gunicorn
├── requirements.txt
├── render.yaml         # Config de deploy Render
├── templates/
│   ├── base.html       # Layout com sidebar + navbar
│   ├── dashboard.html
│   ├── produtos.html
│   ├── produto_form.html
│   ├── movimentacoes.html
│   ├── movimentacao_form.html
│   ├── alertas.html
│   └── relatorios.html
└── static/
    └── css/
    └── js/
```

## Dados de Demonstração

O sistema vem pré-carregado com:
- **8 categorias** (Bebidas, Limpeza, Higiene, Mercearia, etc.)
- **30 produtos** reais de comércio varejista
- **220 movimentações** simuladas nos últimos 45 dias

---

**Base Exata Consultoria** — Dados e Automação para empresas de Capivari, SP.
