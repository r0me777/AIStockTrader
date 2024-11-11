document.getElementById('fetchDataBtn').addEventListener('click', async function () {
    const ticker = document.getElementById('ticker').value;
    const interval = document.getElementById('interval').value;

    // Fetch data from Flask (Assuming endpoint: '/fetch_data')
    const response = await fetch(`/fetch_data?ticker=${ticker}&interval=${interval}`);
    const data = await response.json();

    updateChart(data);
    updateTable(data);
});

// Update Chart.js with new stock data | note done
function updateChart(data) {
    const ctx = document.getElementById('stockChart').getContext('2d');

    const labels = data.map(item => item.date);
    const prices = data.map(item => item.close);

    if (window.stockChart) {
        window.stockChart.destroy();
    }

    window.stockChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Close Price',
                data: prices,
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { type: 'time', time: { unit: 'day' } },
                y: { beginAtZero: false }
            }
        }
    });
}

// Update HTML table with new stock data
function updateTable(data) {
    const tableBody = document.querySelector('#stockTable tbody');
    tableBody.innerHTML = '';  // Clear previous data

    data.forEach(item => {
        const row = document.createElement('tr');
        const dateCell = document.createElement('td');
        const closeCell = document.createElement('td');

        dateCell.textContent = new Date(item.date).toLocaleDateString();
        closeCell.textContent = item.close.toFixed(2);

        row.appendChild(dateCell);
        row.appendChild(closeCell);
        tableBody.appendChild(row);
    });
}

