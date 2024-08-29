function changeStock(ticker) {
    window.location.href = `/stock/${ticker}`;
}

window.onload = function() {
    const ctx = document.getElementById('stockChart').getContext('2d');

    // Sample data, replace with actual data
    const data = {
        labels: [/* Dates here */],
        datasets: [{
            label: 'Stock Prices',
            data: [/* Prices here */],
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
        }]
    };

    new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day'
                    }
                }
            }
        }
    });
};
