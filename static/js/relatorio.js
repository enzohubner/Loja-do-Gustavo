const ctx = document.getElementById('relatorioChart').getContext('2d');
const chart = new Chart(ctx, {
        type: 'line',
        data: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
        datasets: [
            {
            label: 'Vendas Alfajor (mil unidades)',
            data: [50, 75, 100, 120, 90, 130, 140, 150, 120, 100, 90, 110],
            borderColor: '#FF5733',
            backgroundColor: 'rgba(255, 87, 51, 0.2)',
            fill: true,
            tension: 0.4
            },
            {
            label: 'Venda de Bolos (mil unidades)',
            data: [80, 100, 120, 140, 110, 150, 160, 170, 130, 110, 100, 120],
            borderColor: '#3498DB',
            backgroundColor: 'rgba(52, 152, 219, 0.2)',
            fill: true,
            tension: 0.4
            }
        ]
        },
        options: {
        responsive: true,
        plugins: {
            legend: {
            position: 'top'
            },
            tooltip: {
            callbacks: {
                label: function (context) {
                return `${context.dataset.label}: ${context.raw}`;
                }
            }
            }
        },
        scales: {
            x: {
            title: {
                display: true,
                text: 'Meses'
            }
            },
            y: {
            title: {
                display: true,
                text: 'Produção'
            },
            beginAtZero: true
            }
        }
        }
    });