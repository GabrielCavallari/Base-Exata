/**
 * Projeto 4 — Automação de Relatórios | Base Exata
 * Script principal de integração do frontend
 */

/**
 * Formata um valor numérico para a moeda brasileira (R$).
 * @param {number} valor - Valor numérico a ser formatado.
 * @returns {string} Valor formatado.
 */
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

/**
 * Consome a API /api/resumo e preenche os 4 painéis de KPIs gerais.
 */
function carregarResumo() {
    fetch('/api/resumo')
        .then(response => {
            if (!response.ok) throw new Error('Erro ao carregar resumo');
            return response.json();
        })
        .then(data => {
            document.getElementById('valor-total-vendas').textContent = formatarMoeda(data.total_vendas);
            document.getElementById('valor-ticket-medio').textContent = formatarMoeda(data.ticket_medio);
            document.getElementById('valor-categorias').textContent = data.categorias_ativas;
            document.getElementById('valor-fornecedores').textContent = data.fornecedores_ativos;
        })
        .catch(error => console.error('Erro ao carregar dados do resumo:', error));
}

/**
 * Consome a API /api/vendas-por-categoria e renderiza o gráfico de rosca (Doughnut).
 */
function carregarVendasCategoria() {
    fetch('/api/vendas-por-categoria')
        .then(response => {
            if (!response.ok) throw new Error('Erro ao carregar vendas por categoria');
            return response.json();
        })
        .then(data => {
            const ctx = document.getElementById('graficoVendasCategoria').getContext('2d');
            
            // Paleta fixa de 8 cores definida na documentação
            const coresCategorias = [
                '#1A365D', '#D35400', '#008080', '#2C3E50',
                '#E8731A', '#234782', '#00A3A3', '#5D7083'
            ];

            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.map(item => item.nome),
                    datasets: [{
                        data: data.map(item => item.total),
                        backgroundColor: coresCategorias.slice(0, data.length),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '55%',
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                padding: 12,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const index = context.dataIndex;
                                    const item = data[index];
                                    return ` ${item.nome}: ${formatarMoeda(item.total)} (${item.percentual}%)`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Erro ao renderizar gráfico de vendas por categoria:', error));
}

/**
 * Consome a API /api/fechamento-mensal e renderiza o gráfico de barras comparativo de vendas e margens.
 */
function carregarFechamentoMensal() {
    fetch('/api/fechamento-mensal')
        .then(response => {
            if (!response.ok) throw new Error('Erro ao carregar fechamento mensal');
            return response.json();
        })
        .then(data => {
            const ctx = document.getElementById('graficoFechamentoMensal').getContext('2d');

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.map(item => item.mes),
                    datasets: [
                        {
                            label: 'Total Vendas',
                            data: data.map(item => item.total_vendas),
                            backgroundColor: 'rgba(26, 54, 93, 0.8)',
                            borderColor: '#1A365D',
                            borderWidth: 1
                        },
                        {
                            label: 'Margem Estimada',
                            data: data.map(item => item.margem_estimada),
                            backgroundColor: 'rgba(211, 84, 0, 0.7)',
                            borderColor: '#D35400',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    // Eixo formatado com prefixo "R$ " e sufixo "k" para milhares
                                    return 'R$ ' + (value / 1000).toFixed(0) + 'k';
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.dataset.label || '';
                                    const value = context.parsed.y;
                                    return ` ${label}: ${formatarMoeda(value)}`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Erro ao renderizar gráfico de fechamento mensal:', error));
}

/**
 * Consome a API /api/evolucao-ticket e renderiza o gráfico de linha do ticket médio.
 */
function carregarTicket() {
    fetch('/api/evolucao-ticket')
        .then(response => {
            if (!response.ok) throw new Error('Erro ao carregar evolução do ticket');
            return response.json();
        })
        .then(data => {
            const ctx = document.getElementById('graficoTicket').getContext('2d');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.map(item => item.mes),
                    datasets: [{
                        label: 'Ticket Médio (R$)',
                        data: data.map(item => item.ticket_medio),
                        borderColor: '#008080',
                        backgroundColor: 'rgba(0, 128, 128, 0.08)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: 4,
                        pointBackgroundColor: '#1A365D',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: function(value) {
                                    return 'R$ ' + value.toFixed(2).replace('.', ',');
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const value = context.parsed.y;
                                    return ` Ticket Médio: ${formatarMoeda(value)}`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Erro ao renderizar gráfico de evolução de ticket:', error));
}

/**
 * Consome a API /api/ranking-fornecedores e popula a tabela de ranqueamento.
 */
function carregarRankingFornecedores() {
    fetch('/api/ranking-fornecedores')
        .then(response => {
            if (!response.ok) throw new Error('Erro ao carregar ranking de fornecedores');
            return response.json();
        })
        .then(data => {
            const tbody = document.getElementById('tabelaFornecedores');
            tbody.innerHTML = ''; // Limpa conteúdo residual do HTML

            data.forEach((item, index) => {
                const tr = document.createElement('tr');
                
                tr.innerHTML = `
                    <td>
                        <span class="badge-posicao">${index + 1}</span>
                    </td>
                    <td class="fw-semibold text-dark">${item.nome}</td>
                    <td>${item.cidade}</td>
                    <td class="text-end fw-bold text-dark">${formatarMoeda(item.total_compras)}</td>
                    <td class="text-center">${item.num_pedidos}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => console.error('Erro ao povoar tabela de ranking de fornecedores:', error));
}

// Inicializa o consumo das APIs quando o DOM estiver completamente carregado
document.addEventListener('DOMContentLoaded', function() {
    carregarResumo();
    carregarVendasCategoria();
    carregarFechamentoMensal();
    carregarTicket();
    carregarRankingFornecedores();
});
