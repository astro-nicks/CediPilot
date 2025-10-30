const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom', labels: { font: { size: 13 } } },
    title: { display: true, text: 'Monthly Overview', font: { size: 15 } }
  },
  scales: { y: { beginAtZero: true } }
};
