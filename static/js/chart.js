let salesChart = null;

function initializeChart() {
    const today = new Date();
    const startOfYear = new Date(today.getFullYear(), 0, 1);
    const endOfYear = new Date(today.getFullYear(), 11, 31);
    
    document.getElementById('start_date').value = startOfYear.toISOString().split('T')[0];
    document.getElementById('end_date').value = endOfYear.toISOString().split('T')[0];
    
    // Initialize Flowbite multiselect
    const productsSelect = document.getElementById('products');
    productsSelect.options[0].selected = true;
    productsSelect.options[1].selected = true;
    
    // Trigger initial report
    document.getElementById('reportForm').dispatchEvent(new Event('submit'));
}

async function fetchSalesData(startDate, endDate, products) {
    const queryParams = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
    });
    products.forEach(product => queryParams.append('products[]', product));
    
    try {
        const response = await fetch(`/api/sales?${queryParams}`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        return null;
    }
}

function updateChart(data) {
    const ctx = document.getElementById('salesChart').getContext('2d');
    
    if (salesChart) {
        salesChart.destroy();
    }

    const colors = [
        { border: 'rgb(255, 99, 132)', background: 'rgba(255, 99, 132, 0.2)' },
        { border: 'rgb(54, 162, 235)', background: 'rgba(54, 162, 235, 0.2)' },
        { border: 'rgb(75, 192, 192)', background: 'rgba(75, 192, 192, 0.2)' },
        { border: 'rgb(255, 159, 64)', background: 'rgba(255, 159, 64, 0.2)' }
    ];

    const datasets = Object.entries(data).map(([product, values], index) => ({
        label: `${product} (mil unidades)`,
        data: Object.values(values),
        borderColor: colors[index % colors.length].border,
        backgroundColor: colors[index % colors.length].background,
        fill: true,
        tension: 0.4
    }));

    salesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Object.keys(Object.values(data)[0]).map(date => {
                const [year, month] = date.split('-');
                const monthNames = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
                return monthNames[parseInt(month) - 1];
            }),
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Vendas por Produto'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Produção'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Meses'
                    }
                }
            }
        }
    });
}
async function generatePDF() {
    // Get the chart canvas
    const canvas = document.getElementById('salesChart');
    
    // Convert chart to base64 image
    const chartImage = canvas.toDataURL('image/png');
    
    // Get current filter values
    const startDate = document.getElementById('start_date').value;
    const endDate = document.getElementById('end_date').value;
    const products = Array.from(document.getElementById('products').selectedOptions).map(option => option.value);
    
    // Send request to generate PDF
    try {
        const response = await fetch('/generate-pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chart_image: chartImage,
                start_date: startDate,
                end_date: endDate,
                products: products
            })
        });
        
        if (response.ok) {
            // Get the PDF blob
            const blob = await response.blob();
            
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `relatorio-vendas-${startDate}-${endDate}.pdf`;
            
            // Trigger download
            document.body.appendChild(a);
            a.click();
            
            // Cleanup
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        }
    } catch (error) {
        console.error('Error generating PDF:', error);
        alert('Erro ao gerar PDF. Por favor, tente novamente.');
    }
}