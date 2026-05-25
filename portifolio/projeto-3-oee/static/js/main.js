// main.js — Projeto 3 Monitor OEE | Base Exata

// Classifica o valor de OEE (float 0-1) em categoria de desempenho
function classificarOee(valor) {
    if (valor >= 0.85) return 'bom';
    if (valor >= 0.65) return 'atencao';
    return 'critico';
}

// Formata float 0-1 como string percentual com 1 casa decimal
function formatarPct(valor) {
    return (valor * 100).toFixed(1) + '%';
}

// Retorna objeto {fundo, texto} com cores para células do heatmap
function corHeatmap(valor) {
    if (valor === null || valor === undefined) {
        return { fundo: '#6c757d', texto: '#fff' };
    }
    if (valor >= 0.85) {
        return { fundo: '#198754', texto: '#fff' };
    }
    if (valor >= 0.65) {
        return { fundo: '#ffc107', texto: '#000' };
    }
    return { fundo: '#dc3545', texto: '#fff' };
}

// Retorna texto do badge conforme classificação
function textoBadge(classificacao) {
    if (classificacao === 'bom')     return 'Ótimo';
    if (classificacao === 'atencao') return 'Atenção';
    return 'Crítico';
}

// Carrega KPIs de resumo (OEE geral, disponibilidade, performance, qualidade)
function carregarResumo() {
    fetch('/api/resumo')
        .then(function(r) { return r.json(); })
        .then(function(dados) {
            var kpis = {
                'oee':           dados.oee_geral,
                'disponibilidade': dados.disponibilidade,
                'performance':   dados.performance,
                'qualidade':     dados.qualidade
            };

            Object.keys(kpis).forEach(function(chave) {
                var valor = kpis[chave];
                var classe = classificarOee(valor);

                document.getElementById('valor-' + chave).textContent = formatarPct(valor);

                var badge = document.getElementById('badge-' + chave);
                badge.innerHTML = '<span class="badge badge-oee-' + classe + '">' + textoBadge(classe) + '</span>';
            });
        });
}

// Carrega e renderiza gráfico de barras horizontal: OEE por Máquina
function carregarOeeMaquina() {
    fetch('/api/oee-por-maquina')
        .then(function(r) { return r.json(); })
        .then(function(dados) {
            var labels = dados.map(function(d) { return d.nome; });
            var valores = dados.map(function(d) { return parseFloat((d.oee * 100).toFixed(1)); });
            var cores = dados.map(function(d) {
                var classe = classificarOee(d.oee);
                if (classe === 'bom')     return '#3fb950';
                if (classe === 'atencao') return '#d29922';
                return '#f85149';
            });

            var ctx = document.getElementById('graficoOeeMaquina').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'OEE (%)',
                        data: valores,
                        backgroundColor: cores,
                        borderRadius: 4
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return 'OEE: ' + context.parsed.x.toFixed(1) + '%';
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            max: 100,
                            grid: { color: '#30363d' },
                            ticks: {
                                color: '#8b949e',
                                callback: function(valor) { return valor + '%'; }
                            }
                        },
                        y: {
                            grid: { color: '#30363d' },
                            ticks: { color: '#e6edf3' }
                        }
                    }
                }
            });
        });
}

// Carrega e renderiza gráfico de linha: OEE diário dos últimos 30 dias
function carregarHistorico() {
    fetch('/api/oee-historico')
        .then(function(r) { return r.json(); })
        .then(function(dados) {
            var labels = dados.map(function(d) { return d.data; });
            var valores = dados.map(function(d) { return d.oee * 100; });

            var ctx = document.getElementById('graficoOeeHistorico').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'OEE Diário',
                        data: valores,
                        borderColor: '#58a6ff',
                        backgroundColor: 'rgba(88, 166, 255, 0.1)',
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
                            beginAtZero: false,
                            min: 0,
                            max: 100,
                            grid: { color: '#30363d' },
                            ticks: {
                                color: '#8b949e',
                                callback: function(valor) { return valor + '%'; }
                            }
                        },
                        x: {
                            grid: { color: '#30363d' },
                            ticks: { color: '#8b949e' }
                        }
                    }
                }
            });
        });
}

// Carrega e preenche tabela heatmap de OEE por máquina e turno
function carregarHeatmap() {
    fetch('/api/heatmap')
        .then(function(r) { return r.json(); })
        .then(function(dados) {
            var tbody = document.getElementById('tabelaHeatmap');
            tbody.innerHTML = '';

            dados.forEach(function(item) {
                var tr = document.createElement('tr');

                // Coluna com nome da máquina
                var tdMaquina = document.createElement('td');
                tdMaquina.style.padding = '10px 16px';
                tdMaquina.textContent = item.maquina;
                tr.appendChild(tdMaquina);

                // Colunas de turno A, B, C
                ['turno_a', 'turno_b', 'turno_c'].forEach(function(campo) {
                    var valor = item[campo];
                    var cor = corHeatmap(valor);
                    var td = document.createElement('td');
                    td.style.cssText = 'background-color:' + cor.fundo + '; color:' + cor.texto + '; text-align:center; font-weight:600; padding: 10px 16px;';
                    td.textContent = (valor !== null && valor !== undefined) ? formatarPct(valor) : '—';
                    tr.appendChild(td);
                });

                tbody.appendChild(tr);
            });
        });
}

// Inicializa todos os componentes ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    carregarResumo();
    carregarOeeMaquina();
    carregarHistorico();
    carregarHeatmap();
});
