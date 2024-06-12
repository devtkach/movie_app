document.addEventListener('DOMContentLoaded', function() {
    // Colors for the charts
    const colors = [
        'rgba(54, 162, 235, 0.5)',
        'rgba(255, 99, 132, 0.5)',
        'rgba(75, 192, 192, 0.5)',
        'rgba(153, 102, 255, 0.5)',
        'rgba(255, 159, 64, 0.5)',
        'rgba(255, 206, 86, 0.5)',
        'rgba(104, 132, 245, 0.5)',
        'rgba(255, 99, 232, 0.5)',
        'rgba(55, 199, 232, 0.5)',
        'rgba(75, 182, 192, 0.5)',
    ];

    // Genres Chart
    const genresCtx = document.getElementById('genresChart').getContext('2d');
    const genresChart = new Chart(genresCtx, {
        type: 'polarArea',
        data: {
            labels: JSON.parse(document.getElementById('genresLabels').textContent),
            datasets: [{
                label: 'Genres',
                data: JSON.parse(document.getElementById('genresData').textContent),
                backgroundColor: colors,
                borderColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });

    // Ratings Over Decades Chart
    const ratingsDecadesCtx = document.getElementById('ratingsDecadesChart').getContext('2d');
    const ratingsDecadesChart = new Chart(ratingsDecadesCtx, {
        type: 'line',
        data: {
            labels: JSON.parse(document.getElementById('ratingsDecadesLabels').textContent),
            datasets: [{
                label: 'Average Rating',
                data: JSON.parse(document.getElementById('avgRatingsData').textContent),
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    title: {
                        display: true,
                        text: 'Rating'
                    },
                    beginAtZero: true,
                    suggestedMax: 10
                },
                x: {
                    title: {
                        display: true,
                        text: 'Decade'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true
                }
            }
        }
    });
});
