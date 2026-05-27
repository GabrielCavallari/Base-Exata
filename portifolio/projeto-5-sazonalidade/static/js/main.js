/* Javascript principal — Dashboard de Sazonalidade | Base Exata */

document.addEventListener('DOMContentLoaded', () => {
    // Carregar todas as informações assim que o DOM estiver pronto
    carregarResumo();
    carregarSazonalidade();
    carregarSemanal();
    carregarTopProdutos();
    carregarPrevisao();
});

/**
 * Auxiliar para formatar valores numéricos em moeda Real (BRL)
 */
function formatarReais(valor) {
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

/**
 * Busca do endpoint /api/resumo e atualiza os 4 cards de KPI principais
 */
async function carregarResumo() {
    fetch('/api/resumo')
        .then(response => response.json())
        .then(data => {
            document.getElementById('kpi-total-produtos').textContent = data.total_produtos;
            document.getElementById('kpi-vendas-30d').textContent = formatarReais(data.total_vendas_30d);
            document.getElementById('kpi-ticket-30d').textContent = formatarReais(data.ticket_medio_30d);
            document.getElementById('kpi-mais-vendido').textContent = data.produto_mais_vendido;
        })
        .catch(err => console.error('Erro ao carregar dados:', err));
}

/**
 * Busca do endpoint /api/sazonalidade-mensal e renderiza o gráfico de barras
 */
async function carregarSazonalidade() {
    fetch('/api/sazonalidade-mensal')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('grafico-sazonalidade').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.map(d => d.mes),
                    datasets: [{
                        label: 'Quantidade Vendida',
                        data: data.map(d => d.quantidade),
                        backgroundColor: '#1A365D',
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Quantidade (unidades)',
                                font: {
                                    size: 11,
                                    weight: 'bold'
                                }
                            },
                            ticks: {
                                font: {
                                    size: 11
                                }
                            }
                        },
                        x: {
                            ticks: {
                                font: {
                                    size: 11
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        })
        .catch(err => console.error('Erro ao carregar dados:', err));
}

/**
 * Busca do endpoint /api/evolucao-semanal e renderiza o gráfico de linhas
 */
async function carregarSemanal() {
    fetch('/api/evolucao-semanal')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('grafico-semanal').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.map(d => d.semana),
                    datasets: [{
                        label: 'Faturamento',
                        data: data.map(d => d.valor),
                        borderColor: '#008080',
                        backgroundColor: '#008080',
                        tension: 0.3,
                        pointRadius: 3,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return 'R$ ' + value.toLocaleString('pt-BR');
                                },
                                font: {
                                    size: 11
                                }
                            }
                        },
                        x: {
                            ticks: {
                                font: {
                                    size: 11
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        })
        .catch(err => console.error('Erro ao carregar dados:', err));
}

/**
 * Busca do endpoint /api/top-produtos e renderiza o gráfico de rosca
 */
async function carregarTopProdutos() {
    fetch('/api/top-produtos')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('grafico-top-produtos').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.map(d => d.nome),
                    datasets: [{
                        data: data.map(d => d.quantidade_total),
                        backgroundColor: [
                            '#1A365D',
                            '#D35400',
                            '#008080',
                            '#2C3E50',
                            '#E8731A',
                            '#234782',
                            '#00A3A3',
                            '#5D7083'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 12,
                                font: {
                                    size: 10
                                },
                                padding: 8
                            }
                        }
                    }
                }
            });
        })
        .catch(err => console.error('Erro ao carregar dados:', err));
}

/**
 * Busca do endpoint /api/previsao-demanda e popula a tabela de demanda futura
 */
async function carregarPrevisao() {
    fetch('/api/previsao-demanda')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('tbody-previsao');
            tbody.innerHTML = '';
            
            data.forEach(prod => {
                const tr = document.createElement('tr');
                
                // Nome do Produto
                const tdNome = document.createElement('td');
                tdNome.textContent = prod.produto;
                tdNome.className = 'fw-semibold text-start text-dark';
                tr.appendChild(tdNome);
                
                // Categoria com Badge
                const tdCategoria = document.createElement('td');
                tdCategoria.className = 'text-start';
                const spanBadge = document.createElement('span');
                spanBadge.className = 'badge badge-categoria';
                spanBadge.textContent = prod.categoria;
                tdCategoria.appendChild(spanBadge);
                tr.appendChild(tdCategoria);
                
                // Colunas das 12 Previsões Mensais
                prod.previsoes.forEach(prev => {
                    const tdPrev = document.createElement('td');
                    tdPrev.textContent = prev.previsto.toLocaleString('pt-BR');
                    tr.appendChild(tdPrev);
                });
                
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error('Erro ao carregar dados:', err));
}
