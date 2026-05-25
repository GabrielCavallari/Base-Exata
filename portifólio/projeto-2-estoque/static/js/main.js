// main.js — Projeto 2 Gestão de Estoque | Base Exata

// Filtro de busca em tempo real na tabela de produtos
document.addEventListener('DOMContentLoaded', function () {
    const campoBusca = document.getElementById('campoBusca');

    if (campoBusca) {
        campoBusca.addEventListener('input', function () {
            const termo = this.value.toLowerCase().trim();
            const linhas = document.querySelectorAll('#tabelaProdutos tbody .linha-produto');

            linhas.forEach(function (linha) {
                const texto = linha.textContent.toLowerCase();
                linha.style.display = texto.includes(termo) ? '' : 'none';
            });
        });
    }
});
