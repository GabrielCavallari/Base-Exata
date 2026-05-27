# Checklist de Validação das Demos – Base Exata

Este guia contém as validações operacionais e técnicas rápidas que devem ser executadas **30 minutos antes** de qualquer demonstração comercial ao vivo com clientes. O objetivo é garantir o perfeito carregamento das páginas hospedadas na web (Render) e evitar lentidões ou falhas operacionais diante do prospect.

---

## ⚡ 1. Aquecimento de Servidores (Degelo do Render)
Como as aplicações e a landing page estão hospedadas na versão de plano gratuito do Render, os servidores entram em modo de hibernação (sleep) após 15 minutos sem receber acessos.
- [ ] **Acessar a Landing Page:** Abra o site da Base Exata e espere carregar completamente. Se estiver hibernando, a primeira requisição pode demorar de 30 a 50 segundos. **Faça isso antes da reunião para que ela abra de forma instantânea na frente do cliente.**
- [ ] **Aquecer as Demos Selecionadas:** Abra as abas das duas demos que você planejou mostrar no roteiro e aguarde o primeiro carregamento completo.
  * [baseexata-vendas.onrender.com](https://baseexata-vendas.onrender.com) (Vendas)
  * [estoque-app-nzd4.onrender.com](https://estoque-app-nzd4.onrender.com) (Estoque)
  * [baseexata-oee.onrender.com](https://baseexata-oee.onrender.com) (OEE)
  * [baseexata-relatorios.onrender.com](https://baseexata-relatorios.onrender.com) (Relatórios)
  * [baseexata-sazonalidade.onrender.com](https://baseexata-sazonalidade.onrender.com) (Sazonalidade)
  * [baseexata-performance.onrender.com](https://baseexata-performance.onrender.com) (Performance)

---

## 📊 2. Validação Visual e Operacional (Interface)
Nas abas abertas das demos selecionadas, realize os seguintes testes rápidos de cliques:
- [ ] **Os dados aparecem atualizados?** Verifique se o seed automático populou as datas e os valores dos cards recentes (os gráficos e tabelas devem mostrar datas próximas ao ano e mês correntes, não anos antigos).
- [ ] **Os gráficos carregaram perfeitamente?** Verifique se os componentes do Chart.js renderizaram sem quebras de layout ou sobreposição de legendas.
- [ ] **Os menus laterais (sidebars) funcionam?** Clique nos links dos menus para navegar pelas telas internas da aplicação (ex: clicar em "Produtos", "Movimentações" e "Alertas" no `estoque-app`). A transição deve ser limpa e sem erros 404/500.
- [ ] **Os cards de KPIs exibem os valores corretos?** Os valores numéricos nos cards principais (faturamento total, ticket médio, OEE, alertas de estoque mínimo) devem estar populados e formatados corretamente como moeda (R$), porcentagem (%) ou inteiros.

---

## 🔗 3. Validação de Links e Integrações (Landing Page)
- [ ] **Links do Portfólio Funcionam?** Na seção de Portfólio da Landing Page, clique nos botões das demos para garantir que os links diretos para os deploys do Render estão atualizados e apontando para os endereços corretos.
- [ ] **Links do README Funcionam?** Se você for demonstrar o código ou o repositório principal no GitHub, certifique-se de que os links de navegação entre a documentação principal e a pasta `docs/apresentacao/` carreguem sem problemas de caminhos quebrados.
- [ ] **Botão de WhatsApp e FormSubmit ativos:**
  * O botão flutuante de WhatsApp deve abrir o redirecionador de link apontando para o número comercial correto.
  * O formulário de contato de leads deve exibir a tela de sucesso da Base Exata (`sucesso.html`) ao simular um envio opcional.
