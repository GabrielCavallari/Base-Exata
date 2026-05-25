// Lógica de Integração Frontend — Projeto 6 Performance Comercial | Base Exata

document.addEventListener("DOMContentLoaded", () => {
    // Inicializar chamadas da API Flask
    carregarResumo();
    carregarRanking();
    inicializarGraficos();
});

// Formatador de Moeda Real (R$)
const formatarMoeda = (valor) => {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
};

// 1. Carrega os cards de KPI superiores
function carregarResumo() {
    fetch("/api/resumo")
        .then(response => response.json())
        .then(data => {
            document.getElementById("kpi-faturamento").innerText = formatarMoeda(data.faturamento_total);
            document.getElementById("kpi-conversao").innerText = `${data.taxa_conversao}%`;
            document.getElementById("kpi-lider").innerText = data.melhor_vendedor;
            document.getElementById("kpi-lider-faturamento").innerHTML = `Faturamento no mês: <strong>${formatarMoeda(data.faturamento_lider)}</strong>`;
            document.getElementById("kpi-meta-global").innerText = `${data.atingimento_global}%`;
            
            // Adiciona classe de cor na meta global com base no resultado
            const metaGlobalElement = document.getElementById("kpi-meta-global");
            if (data.atingimento_global >= 100) {
                metaGlobalElement.style.color = "var(--accent)";
            } else if (data.atingimento_global >= 90) {
                metaGlobalElement.style.color = "var(--info)";
            } else {
                metaGlobalElement.style.color = "var(--danger)";
            }
        })
        .catch(err => {
            console.error("Erro ao carregar resumo dos KPIs:", err);
        });
}

// 2. Carrega a tabela de ranking de vendedores
function carregarRanking() {
    fetch("/api/ranking-vendedores")
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById("tabela-ranking-corpo");
            tbody.innerHTML = ""; // Limpa a linha de loading

            data.forEach((vendedor, index) => {
                const posicao = index + 1;
                
                // Determinar classes CSS e Badges baseadas no % de atingimento da meta
                let badgeStatus = "";
                let colorClass = "";
                
                if (vendedor.percentual_atingimento >= 100) {
                    badgeStatus = `<span class="badge-status badge-status-success"><i class="bi bi-check-circle-fill"></i> Meta Batida</span>`;
                    colorClass = "bg-success";
                } else if (vendedor.percentual_atingimento >= 90) {
                    badgeStatus = `<span class="badge-status badge-status-warning"><i class="bi bi-exclamation-circle-fill"></i> Próximo</span>`;
                    colorClass = "bg-primary"; // Utiliza cor azul secundária do sistema
                } else {
                    badgeStatus = `<span class="badge-status badge-status-danger"><i class="bi bi-x-circle-fill"></i> Insuficiente</span>`;
                    colorClass = "bg-danger";
                }

                // Capped progress width para exibição correta na barra de progresso (máximo 100%)
                const progressWidth = Math.min(vendedor.percentual_atingimento, 100);

                // Destaque para as 3 primeiras posições no ranking
                let medalha = "";
                if (posicao === 1) {
                    medalha = `<span class="fs-5 text-warning" title="1º Lugar"><i class="bi bi-trophy-fill"></i></span>`;
                } else if (posicao === 2) {
                    medalha = `<span class="fs-5 text-secondary" title="2º Lugar"><i class="bi bi-award-fill"></i></span>`;
                } else if (posicao === 3) {
                    medalha = `<span class="fs-5" style="color: #cd7f32;" title="3º Lugar"><i class="bi bi-award-fill"></i></span>`;
                } else {
                    medalha = `<span class="text-muted fw-bold">${posicao}º</span>`;
                }

                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td class="text-center">${medalha}</td>
                    <td><strong style="color: var(--primary-light);">${vendedor.nome}</strong></td>
                    <td><span class="badge bg-light text-dark border">${vendedor.regiao}</span></td>
                    <td class="text-end text-muted font-monospace">${formatarMoeda(vendedor.meta_mensal)}</td>
                    <td class="text-end text-muted font-monospace">${formatarMoeda(vendedor.meta_total_6meses)}</td>
                    <td class="text-end font-monospace fw-bold" style="color: var(--primary-light);">${formatarMoeda(vendedor.total_faturado)}</td>
                    <td>
                        <div class="progress-container-custom">
                            <div class="d-flex justify-content-between font-monospace" style="font-size: 10.5px;">
                                <span>Atingido:</span>
                                <strong class="text-dark">${vendedor.percentual_atingimento}%</strong>
                            </div>
                            <div class="progress-custom">
                                <div class="progress-bar-custom ${colorClass}" style="width: ${progressWidth}%"></div>
                            </div>
                        </div>
                    </td>
                    <td class="text-center">${badgeStatus}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => {
            console.error("Erro ao carregar ranking de vendedores:", err);
            const tbody = document.getElementById("tabela-ranking-corpo");
            tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-danger"><i class="bi bi-exclamation-triangle-fill"></i> Erro ao obter dados do ranking comercial.</td></tr>`;
        });
}

// 3. Inicializa os gráficos usando Chart.js
function inicializarGraficos() {
    // A) Gráfico de Evolução de Metas (Barras Agrupadas)
    fetch("/api/evolucao-metas")
        .then(response => response.json())
        .then(data => {
            const labels = data.map(item => item.mes);
            const realizado = data.map(item => item.realizado);
            const meta = data.map(item => item.meta);

            const ctx = document.getElementById("chart-evolucao").getContext("2d");
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Faturamento Realizado (R$)',
                            data: realizado,
                            backgroundColor: '#10b981', // Verde Esmeralda
                            borderRadius: 6,
                            borderWidth: 0,
                            barPercentage: 0.8,
                            categoryPercentage: 0.7
                        },
                        {
                            label: 'Meta Planejada (R$)',
                            data: meta,
                            backgroundColor: '#94a3b8', // Cinza Slate
                            borderRadius: 6,
                            borderWidth: 0,
                            barPercentage: 0.8,
                            categoryPercentage: 0.7
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                boxWidth: 12,
                                usePointStyle: true,
                                font: {
                                    family: "'Inter', sans-serif",
                                    size: 12,
                                    weight: 500
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    let label = context.dataset.label || '';
                                    if (label) {
                                        label += ': ';
                                    }
                                    if (context.raw !== null) {
                                        label += formatarMoeda(context.raw);
                                    }
                                    return label;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: '#f1f5f9'
                            },
                            ticks: {
                                font: {
                                    family: "'Inter', sans-serif",
                                    size: 11
                                },
                                callback: function(value) {
                                    return value >= 1000 ? (value / 1000) + 'k' : value;
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                font: {
                                    family: "'Inter', sans-serif",
                                    size: 11,
                                    weight: 500
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(err => {
            console.error("Erro ao renderizar gráfico de evolução de metas:", err);
        });

    // B) Gráfico de Faturamento por Região (Doughnut)
    fetch("/api/vendas-regiao")
        .then(response => response.json())
        .then(data => {
            const labels = data.map(item => item.regiao);
            const valores = data.map(item => item.total);

            const ctx = document.getElementById("chart-regioes").getContext("2d");
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: valores,
                        backgroundColor: [
                            '#1e3a8a', // Azul Escuro
                            '#10b981', // Verde Esmeralda
                            '#0ea5e9', // Azul Sky
                            '#f59e0b', // Laranja Amber
                            '#8b5cf6', // Roxo Violet
                            '#ec4899'  // Rosa
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff',
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 10,
                                padding: 12,
                                usePointStyle: true,
                                font: {
                                    family: "'Inter', sans-serif",
                                    size: 11,
                                    weight: 500
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const valor = context.raw || 0;
                                    
                                    // Calcular porcentagem
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentual = ((valor / total) * 100).toFixed(1);
                                    
                                    return ` ${label}: ${formatarMoeda(valor)} (${percentual}%)`;
                                }
                            }
                        }
                    },
                    cutout: '65%' // Layout rosca elegante
                }
            });
        })
        .catch(err => {
            console.error("Erro ao renderizar gráfico de faturamento por região:", err);
        });
}
