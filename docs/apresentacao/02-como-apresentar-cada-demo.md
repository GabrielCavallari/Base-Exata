# 02. Guia de Apresentação das Demos – Base Exata

Este guia orienta o consultor a realizar demonstrações (demos) de alto impacto para cada um dos 7 sistemas estabilizados da Base Exata. Cada seção detalha o alinhamento estratégico da demo com o perfil e as dores do cliente, garantindo uma abordagem de venda extremamente consultiva e focada em valor real de negócios.

---

## 💻 1. Landing Page Institucional
A porta de entrada digital da consultoria. Mostra aos prospects como eles podem construir uma presença digital moderna e profissional na internet.

* **🎯 Dor que representa:** Falta de presença digital profissional, site desatualizado, dificuldade de captar contatos online de forma automatizada ou dependência exclusiva de redes sociais (Instagram/Facebook) que mudam o algoritmo constantemente.
* **🏢 Perfil de Cliente Ideal:** Empresas locais de serviços (clínicas, escritórios, consultórios, instaladores, restaurantes) e comércios que querem ser encontrados no Google por clientes da região de Capivari.
* **✨ O que mostrar primeiro (UAU!):** 
  * O design responsivo abrindo perfeitamente no celular.
  * O botão de WhatsApp flutuante que direciona o lead imediatamente para o fechamento.
  * O formulário de contato integrado que envia as informações de prospecção direto para o e-mail ou planilha do cliente sem custos de ferramentas caras.
* **⚠️ O que evitar falar/mostrar:** Evite detalhar termos como "HTML estático", "Tailwind CSS", "Alpine.js" ou "Schema.org". Não entre no código do formulário FormSubmit.
* **🔗 Pergunta de Conexão:** 
  > *"Hoje, quando um cliente na região de Capivari busca pelos seus serviços no Google, o que ele encontra? Você já perdeu algum cliente por não ter uma página profissional ou rápida que explicasse claramente os seus diferenciais?"*

---

## 📦 2. Sistema de Gestão de Estoque (`estoque-app`)
A demo mais completa de sistema interno da Base Exata. Simula o controle operacional do dia a dia de mercadorias.

* **🎯 Dor que representa:** Furos no estoque físico, perda de mercadoria por vencimento ou obsolescência, compras em excesso que travam o caixa da empresa, ou falta de saber se o estoque mínimo de um item crítico foi atingido antes que ele acabe.
* **🏢 Perfil de Cliente Ideal:** Comércios varejistas, distribuidores locais, autopeças, pequenos mercados e microindústrias locais que controlam estoque em fichas de papel ou planilhas difíceis de atualizar.
* **✨ O que mostrar primeiro (UAU!):**
  * O painel inicial (Dashboard) com o card vermelho piscando de **"Alertas de Estoque Mínimo"** ou **"Itens Críticos"**.
  * A facilidade de realizar uma Entrada ou Saída com dois cliques, atualizando o saldo na hora.
  * A tabela limpa com buscas rápidas de produtos por categoria.
* **⚠️ O que evitar falar/mostrar:** Evite falar sobre a base de dados em SQLite ou sobre frameworks backend (Flask/Python). Não gaste muito tempo mostrando o cadastro completo de campos complexos; foque na simplicidade do dia a dia operacional.
* **🔗 Pergunta de Conexão:**
  > *"Você já passou pela situação frustrante de vender um produto ao cliente e, na hora de entregar, descobrir que ele não estava na prateleira física? Ou de ver dinheiro parado na prateleira em produtos que não giram há meses?"*

---

## 📊 3. Dashboard de Inteligência de Vendas
Painel voltado para dar clareza analítica sobre o faturamento do negócio.

* **🎯 Dor que representa:** Gestor "no escuro" em relação aos números da empresa. Falta de clareza sobre qual produto dá mais lucro, se o faturamento está crescendo ou caindo em relação ao mês passado, e qual o ticket médio gasto pelos clientes.
* **🏢 Perfil de Cliente Ideal:** Lojas de roupas, restaurantes, pequenos mercados e comércios em geral que já emitem notas fiscais ou cupons de vendas, mas não usam esses dados para tomar decisões estratégicas.
* **✨ O que mostrar primeiro (UAU!):**
  * O gráfico interativo de linha que mostra a evolução das vendas semanais de forma limpa.
  * O ranking dos **Top 5 Produtos mais Vendidos** e sua representatividade no faturamento.
  * O cálculo dinâmico do **Ticket Médio** e como uma pequena variação desse indicador muda o resultado no fim do mês.
* **⚠️ O que evitar falar/mostrar:** Evite falar sobre "APIs JSON", bibliotecas de gráficos (Chart.js) ou queries SQL. Mantenha o foco em "clareza dos números" e "inteligência de negócios".
* **🔗 Pergunta de Conexão:**
  > *"Se você precisasse me dizer hoje, sem abrir nenhuma planilha ou sistema lento, qual foi o seu produto mais rentável no último mês e qual o dia da semana em que você mais vendeu, você teria essa resposta na ponta da língua?"*

---

## 🏭 4. Monitor de Eficiência Industrial (OEE)
Painel especializado no chão de fábrica e na produtividade de máquinas e equipes.

* **🎯 Dor que representa:** Máquinas paradas sem motivo documentado, falta de controle sobre o ritmo da produção, alto índice de peças com defeito (refugo) e falta de saber se a fábrica está operando na capacidade correta para justificar novas contratações ou investimentos.
* **🏢 Perfil de Cliente Ideal:** Pequenas metalúrgicas, confecções de roupas, indústrias de cerâmica, marcenarias industriais e oficinas locais da região.
* **✨ O que mostrar primeiro (UAU!):**
  * O painel visual de **Eficiência Geral (OEE %)** com a barra de progresso colorida (Verde/Amarelo/Vermelho).
  * O histórico diário de perdas e o mapa de calor que mostra em qual turno ou máquina ocorrem as maiores falhas de disponibilidade ou performance.
  * A separação clara entre as 3 grandes perdas: Disponibilidade, Performance e Qualidade.
* **⚠️ O que evitar falar/mostrar:** Evite termos de engenharia de software ou jargões industriais excessivamente teóricos no início. Foque em: "tempo que a máquina ficou parada gerando prejuízo".
* **🔗 Pergunta de Conexão:**
  > *"Hoje, quando uma máquina na sua produção para por quebra ou falta de insumo, como você acompanha o impacto acumulado disso no final do mês? Você sabe quanto custa cada hora de fábrica ociosa no seu negócio?"*

---

## 📑 5. Automação de Relatórios Gerenciais
Simulação de uma rotina automática de consolidação e exportação de dados analíticos.

* **🎯 Dor que representa:** Desperdício de tempo de analistas ou do próprio gestor (horas/dias por semana) abrindo vários sistemas, copiando dados, colando em planilhas do Excel e gerando PDFs manuais para enviar aos sócios ou fornecedores.
* **🏢 Perfil de Cliente Ideal:** Empresas familiares com sócios distantes, administradoras de imóveis, distribuidoras com relatórios semanais de fechamento, ou qualquer empresa onde o gestor gaste o domingo à noite preparando relatórios de fechamento.
* **✨ O que mostrar primeiro (UAU!):**
  * A consolidação de tabelas complexas de faturamento por categoria e fornecedor em uma única tela de leitura limpa.
  * O tempo economizado ao ter dados unificados automaticamente, sem a necessidade de digitação ou fórmulas de Procv/Xlookup que quebram o tempo todo.
* **⚠️ O que evitar falar/mostrar:** Evite falar sobre a lógica dos scripts de consolidação, bibliotecas Python (Pandas/Openpyxl). Foque em: **"eliminação total do retrabalho manual diário"**.
* **🔗 Pergunta de Conexão:**
  > *"Quantas horas por semana você ou sua equipe gastam abrindo sistemas, exportando planilhas, cruzando dados e montando relatórios no Excel para enviar para os sócios ou diretoria? E se esse processo demorasse zero segundos?"*

---

## 📈 6. Análise de Sazonalidade e Demanda
Painel analítico focado em tendências de mercado e compras inteligentes.

* **🎯 Dor que representa:** Compras erradas (comprar muito estoque em meses fracos de vendas, ou comprar pouco e sofrer com a falta de produtos em meses de pico), falta de previsão de caixa necessário para pagar fornecedores antes de datas sazonais e promoções ineficientes em períodos de baixa histórica.
* **🏢 Perfil de Cliente Ideal:** Comércio de calçados, lojas de presentes, mercados, comércios de produtos sazonais (sorveterias, chocolates, vestuário de inverno) ou empresas com faturamento muito instável ao longo do ano.
* **✨ O que mostrar primeiro (UAU!):**
  * O gráfico de sazonalidade comparativo entre o histórico de vendas de anos anteriores e a tendência projetada para os próximos meses.
  * A identificação visual de picos e vales de demanda por categorias específicas de produtos, mostrando quando puxar o freio nas compras ou quando abastecer o estoque antes do pico.
* **⚠️ O que evitar falar/mostrar:** Não comente sobre algoritmos de previsão estatística ou machine learning. Foque apenas em: **"olhar o passado de forma inteligente para prever as compras do futuro"**.
* **🔗 Pergunta de Conexão:**
  > *"Como você define as quantidades de compras com os seus fornecedores para os meses de final de ano ou datas sazonais? É no 'feeling' ou você tem um histórico claro e visual de picos de demanda que te guia para não errar a mão e faltar ou sobrar mercadoria?"*

---

## 🏆 7. Painel de Performance Comercial
Painel focado no acompanhamento de equipes de vendas e metas individuais e coletivas.

* **🎯 Dor que representa:** Vendedores desmotivados por falta de visibilidade sobre suas metas, gestor sem saber quem está performando bem ou mal, dificuldade de calcular comissões de forma transparente e rápida no fim do mês, e ausência de uma cultura de foco em resultados na equipe.
* **🏢 Perfil de Cliente Ideal:** Empresas que trabalham com equipes de vendas externas ou internas (distribuidoras, prestadoras de serviços de telecom, imobiliárias, concessionárias ou comércios com vários atendentes comissionados).
* **✨ O que mostrar primeiro (UAU!):**
  * O ranking de vendedores interativo (com pódio visual) que estimula a competição saudável na equipe.
  * O indicador de **Atingimento de Meta (Meta vs. Realizado)** individual de cada vendedor com cores intuitivas.
  * O faturamento dividido por regiões de atendimento, destacando onde estão os melhores clientes.
* **⚠️ O que evitar falar/mostrar:** Não comente sobre as estruturas de tabelas relacionais do banco ou regras complexas de códigos. Foque no benefício comportamental de ter metas visíveis e clareza para a equipe comercial.
* **🔗 Pergunta de Conexão:**
  > *"Como a sua equipe comercial acompanha as metas diárias ou mensais de vendas hoje? Eles sabem exatamente, em tempo real, quanto falta para atingir a meta e garantir a comissão deles, ou só descobrem isso no fechamento do mês, quando já é tarde demais para correr atrás?"*
