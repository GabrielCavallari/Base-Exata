// main.js — Projeto 1 Dashboard de Vendas | Base Exata

// Formata valor numérico como moeda BRL
function formatarMoeda(valor) {
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

// Formata data de YYYY-MM-DD para DD/MM/YYYY
function formatarData(dataStr) {
    var partes = dataStr.split('-');
    return partes[2] + '/' + partes[1] + '/' + partes[0];
}

// Retorna badge HTML conforme status da venda
function badgeStatus(status) {
    if (status === 'Concluída') {
        return '<span class="badge bg-success">Concluída</span>';
    } else if (status === 'Cancelada') {
        return '<span class="badge bg-danger">Cancelada</span>';
    } else {
        return '<span class="badge bg-warning text-dark">' + status + '</span>';
    }
}

// Carrega e renderiza gráfico de faturamento diário (linha)
function carregarFaturamentoDiario() {
    fetch('/api/faturamento-diario')
        .then(function(r) { return r.json(); })
        .then(function(dados) {
            var ctx = document.getElementById('graficoFaturamentoDiario').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dados.labels,
                    datasets: [{
                        label: 'Faturamento (R$)',
                        data: dados.valores,
                        borderColor: '#008080',
                        backgroundColor: 'rgba(0, 128, 128, 0.10)',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 2,
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(valor) {
                                    return 'R$ ' + valor.toLocaleString('pt-BR');
                                }
                            }
                        }
                    }
                }
            });
        });
}

// Carrega e renderiza gráfico de participação por categoria (doughnut)
function carregarCategorias() {
    fetch('/api/categorias')
        .then(function(r) { return r.json(); })
        .then(function(dados) {
            var ctx = document.getElementById('graficoCategorias').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: dados.labels,
                    datasets: [{
                        data: dados.valores,
                        backgroundColor: [
                            '#1A365D',
                            '#D35400',
                            '#008080',
                            '#2C3E50',
                            '#E8731A',
                            '#234782'
                        ],
                        borderWidth: 2,
                        borderColor: '#F8F9FA'
                    }]
                },
                options: {
                    responsive: true,
                    cutout: '60%',
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        });
}

// Carrega e renderiza gráfico de top 10 produtos (barra horizontal)
function carregarTopProdutos() {
    fetch('/api/top-produtos')
        .then(function(r) { return r.json(); })
        .then(function(dados) {
            var ctx = document.getElementById('graficoTopProdutos').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: dados.labels,
                    datasets: [{
                        label: 'Receita (R$)',
                        data: dados.valores,
                        backgroundColor: 'rgba(26, 54, 93, 0.8)',
                        borderRadius: 4
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(valor) {
                                    return 'R$ ' + valor.toLocaleString('pt-BR');
                                }
                            }
                        }
                    }
                }
            });
        });
}

// Carrega e preenche tabela de últimas vendas
function carregarUltimasVendas() {
    fetch('/api/ultimas-vendas')
        .then(function(r) { return r.json(); })
        .then(function(vendas) {
            var tbody = document.getElementById('tabelaUltimasVendas');
            tbody.innerHTML = '';

            vendas.forEach(function(venda) {
                var tr = document.createElement('tr');
                tr.innerHTML =
                    '<td>' + venda.id + '</td>' +
                    '<td>' + venda.produto + '</td>' +
                    '<td>' + venda.categoria + '</td>' +
                    '<td>' + venda.quantidade + '</td>' +
                    '<td>' + formatarMoeda(venda.preco_unitario) + '</td>' +
                    '<td>' + formatarMoeda(venda.total) + '</td>' +
                    '<td>' + formatarData(venda.data_venda) + '</td>' +
                    '<td>' + badgeStatus(venda.status) + '</td>';
                tbody.appendChild(tr);
            });
        });
}

// Inicializa todos os componentes ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    carregarFaturamentoDiario();
    carregarCategorias();
    carregarTopProdutos();
    carregarUltimasVendas();
});
