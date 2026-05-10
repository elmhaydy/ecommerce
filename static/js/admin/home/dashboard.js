document.addEventListener("DOMContentLoaded", () => {
    const jsonElement = document.getElementById("dashboard-json");

    if (!jsonElement || typeof Chart === "undefined") {
        console.log("Dashboard chart not loaded");
        return;
    }

    const data = JSON.parse(jsonElement.textContent);

    const textColor = getComputedStyle(document.documentElement)
        .getPropertyValue("--text-muted")
        .trim() || "#94a3b8";

    const borderColor = getComputedStyle(document.documentElement)
        .getPropertyValue("--border-color")
        .trim() || "#334155";

    Chart.defaults.color = textColor;
    Chart.defaults.font.family = "Inter, system-ui, sans-serif";

    const overviewChart = document.getElementById("overviewChart");
    const ordersChart = document.getElementById("ordersChart");
    const topProductsChart = document.getElementById("topProductsChart");

    if (overviewChart) {
        new Chart(overviewChart, {
            type: "bar",
            data: {
                labels: ["Produits", "Catégories", "Commandes", "Users"],
                datasets: [{
                    data: [
                        data.overview.products,
                        data.overview.categories,
                        data.overview.orders,
                        data.overview.users
                    ],
                    backgroundColor: [
                        "rgba(124,58,237,.85)",
                        "rgba(6,182,212,.85)",
                        "rgba(34,197,94,.85)",
                        "rgba(245,158,11,.85)"
                    ],
                    borderRadius: 14
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: borderColor }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }

    if (ordersChart) {
        new Chart(ordersChart, {
            type: "doughnut",
            data: {
                labels: ["En attente", "Payées", "Livrées", "Annulées"],
                datasets: [{
                    data: [
                        data.orders.pending,
                        data.orders.paid,
                        data.orders.delivered,
                        data.orders.cancelled
                    ],
                    backgroundColor: [
                        "#f59e0b",
                        "#3b82f6",
                        "#22c55e",
                        "#ef4444"
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "68%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { usePointStyle: true }
                    }
                }
            }
        });
    }

    if (topProductsChart) {
        new Chart(topProductsChart, {
            type: "line",
            data: {
                labels: data.top_products.map(item => item.name),
                datasets: [{
                    data: data.top_products.map(item => item.sold),
                    borderColor: "#7c3aed",
                    backgroundColor: "rgba(124,58,237,.15)",
                    tension: .45,
                    fill: true,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: borderColor }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
});